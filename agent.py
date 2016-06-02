from collections import deque
import atexit
import logging
import logging.config

from app import app, db, Reading, Sensor

if app.config['DEBUG']:
    from w1sim import W1Sim
    ids = ['000001efbab6', '000001efd9ac', '000001eff556']
    W1 = W1Sim(ids)
else:
    from w1thermsensor import W1ThermSensor as W1
    import uwsgi
    import RPi.GPIO as GPIO


class Agent:

    def __init__(self, target_temp):
        self._target_temp = target_temp
        self._timestep = 0
        self._MIN_VALID_TEMP = -5.0
        self._MAX_VALID_TEMP = 30.0
        self._READING_TICK = 5
        self._DELTA_OVERSHOOT_TEMP = 2.0
        self._SSR_PIN = 11
        self._compressor_state = True
        self._sensors = {}
        self._sensors['000001efbab6'] = 'top'
        self._sensors['000001efd9ac'] = 'bottom'
        self._sensors['000001eff556'] = 'beer'
        self._sensor_readings = deque(
            maxlen=int(60/self._READING_TICK)*len(W1.get_available_sensors())
        )

        logging.config.dictConfig(app.config['LOG_CONFIG'])
        self.logger = logging.getLogger('agent')

        if not app.config['DEBUG']:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self._SSR_PIN, GPIO.OUT)
            uwsgi.register_signal(9000, 'worker', self.run)
            uwsgi.add_timer(9000, 5)
            atexit.register(lambda: self.cleanup())
            self.logger.setLevel(logging.WARN)
        else:
            self.logger.setLevel(logging.DEBUG)

        self.logger.info("Agent started")
    
    def set_target_temp(self, temp):
        self._target_temp = temp

    def get_target_temp(self):
        return self._target_temp

    def get_compressor_state(self):
        return self._compressor_state

    def run(self, num):
        self._timestep += self._READING_TICK
        self.logger.debug("Current timestep: " + str(self._timestep))
        if self._timestep >= 60:
            self._timestep = 0
            self.evaluate()
            self.save_reading()

    def save_reading(self):
        reading = Reading(
            target_temp=self.get_target_temp(),
            compressor_state=self.get_compressor_state()
        )
        for w1sensor in W1.get_available_sensors():
            sensor = Sensor(
                placement=self._sensors.get(w1sensor.id),
                value=w1sensor.get_temperature()
            )
            db.session.add(sensor)
            reading.sensors.append(sensor)
        db.session.add(reading)
        db.session.commit()

    def valid_sensor_range(self, value):
        valid = value > self._MIN_VALID_TEMP and value < self._MAX_VALID_TEMP
        if not valid:
            self.logger.error("Sensor value " + str(value) + "is outside possible values")
        return valid

    def evaluate(self):
        sensor_readings = []
        for sensor in W1.get_available_sensors():
            sensor_readings.append(sensor.get_temperature())
        average_temp = sum(sensor_readings)/len(sensor_readings)
        self.logger.debug("Average temp: " + str(average_temp) + ". Target temp:" + str(self.get_target_temp()))
        if average_temp > self.get_target_temp() + self._DELTA_OVERSHOOT_TEMP:
            self.logger.debug("Turn on compressor if needed")
            self._compressor_state = True
            if app.config['DEBUG']:
                return
            if not GPIO.input(self._SSR_PIN):
                self.logger.info("Turning on compressor")
                GPIO.output(self._SSR_PIN, True)
                if not GPIO.input(self._SSR_PIN):
                    self.logger.error("Unable to turn on compressor!")
                    self._compressor_state = False

        if average_temp <= self.get_target_temp():
            self.logging.debug("Turn off compressor if needed")
            self._compressor_state = False
            if app.config['DEBUG']:
                return
            if GPIO.input(self._SSR_PIN):
                GPIO.output(self._SSR_PIN, False)
                self.logger.info("Turning off compressor")
                if GPIO.input(self._SSR_PIN):
                    self.logger.error("Unable to turn off compressor!")
                    self._compressor_state = True

    def cleanup(self):
        self.logger.warn("Program shut down. Cleaning up")
        GPIO.cleanup()
