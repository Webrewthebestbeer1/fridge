from collections import deque
#from apscheduler.scheduler import Scheduler
import atexit
import uwsgi
import RPi.GPIO as GPIO

from app import app, db, Reading, Sensor

if (app.config['DEBUG']):
    from w1sim import W1Sim
    ids = ['000001efbab6', '000001efd9ac', '000001eff556']
    W1 = W1Sim(ids)
else:
    from w1thermsensor import W1ThermSensor as W1



class Agent:
    
    
    def __init__(self, target_temp):
        self._target_temp = target_temp
        self._timestep = 0
        self._MIN_VALID_TEMP = -5.0
        self._MAX_VALID_TEMP = 30.0
        self._READING_TICK = 5
        self._DELTA_OVERSHOOT_TEMP = 2.0
        self._compressor_state = True
        self._sensors = {}
        self._sensors['000001efbab6'] = 'top'
        self._sensors['000001efd9ac'] = 'bottom'
        self._sensors['000001eff556'] = 'beer'
        self._sensor_readings = deque(
            maxlen=int(60/self._READING_TICK)*len(W1.get_available_sensors())
        )
        
        #scheduler = Scheduler(daemon=False)
        #scheduler.add_interval_job(self.run, seconds=self._READING_TICK)
        #scheduler.start()

        self.SSR_PIN = 11

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.SSR_PIN, GPIO.OUT)

        uwsgi.register_signal(9000, 'worker', self.run)
        uwsgi.add_timer(9000, 5)


    def set_target_temp(self, temp):
        self._target_temp = temp

    def get_target_temp(self):
        return self._target_temp

    def get_compressor_state(self):
        return self._compressor_state

    def run(self, num):
        self._timestep += self._READING_TICK
        print(self._timestep)
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
        #if not valid: logger.warn("Sensor value outside possible values:", value)
        return valid

    def evaluate(self):
        sensor_readings = []
        for sensor in W1.get_available_sensors():
            sensor_readings.append(sensor.get_temperature())
        average_temp = sum(sensor_readings)/len(sensor_readings)
        print(average_temp, self.get_target_temp())
        if average_temp > self.get_target_temp() + self._DELTA_OVERSHOOT_TEMP:
            print("turn on compressor if needed")
            self._compressor_state = True
            
            if not GPIO.input(self.SSR_PIN):
                #logger.info("Turning on compressor")
                print("Turning on compressor")
                GPIO.output(self.SSR_PIN, True)
            
        if average_temp <= self.get_target_temp():
            print("turn off compressor if needed")
            self._compressor_state = False
            
            if GPIO.input(self.SSR_PIN):
                GPIO.output(self.SSR_PIN, False)
                #logger.info("Turning off compressor")
                print("Turning off compressor")
            
    def cleanup(self):
        GPIO.cleanup()

    #atexit.register(lambda: cron.shutdown(wait=False))
    atexit.register(lambda: self.cleanup())
