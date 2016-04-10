from w1thermsensor import W1ThermSensor as W1
import RPi.GPIO as GPIO
from collections import deque
from time import sleep
import logging
import logging.config
import loggly.handlers
import sys

logging.config.fileConfig("python.conf")
logger = logging.getLogger("fridge")

DESIRED_TEMP = 16.0
DELTA_OVERSHOOT_TEMP = 2.0
MIN_VALID_TEMP = 0.0
MAX_VALID_TEMP = 30.0
READING_TICK = 5
SSR_PIN = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SSR_PIN, GPIO.OUT)

timestep = 0
sensor_top = W1(W1.THERM_SENSOR_DS18B20, "000001efbab6")
sensor_bottom = W1(W1.THERM_SENSOR_DS18B20, "000001efd9ac")
sensor_beer = W1(W1.THERM_SENSOR_DS18B20, "000001eff556")
sensor_readings = deque(maxlen=int(60/READING_TICK)*3)

def valid_sensor_range(value):
    valid = value > MIN_VALID_TEMP and value < MAX_VALID_TEMP
    if not valid: logger.warn("Sensor value outside possible values:", value)
    return valid

print("Desired temperature:", DESIRED_TEMP, "\n")

try:
    while True:
        sensor_top_value = sensor_top.get_temperature()
        sensor_bottom_value = sensor_bottom.get_temperature()
        sensor_beer_value = sensor_beer.get_temperature()
        if valid_sensor_range(sensor_top_value) and valid_sensor_range(sensor_bottom_value) and valid_sensor_range(sensor_beer_value):
            sensor_readings.append(sensor_top_value)
            sensor_readings.append(sensor_bottom_value)
            sensor_readings.append(sensor_beer_value)
            timestep += READING_TICK
        average_temp = sum(sensor_readings) / len(sensor_readings)
        logger.info("Top sensor temperature: " + str(sensor_top_value))
        print("Top sensor temperature:", sensor_top_value)
        logger.info("Bottom sensor temperature: " + str(sensor_bottom_value))
        print("Bottom sensor temperature:", sensor_bottom_value)
        logger.info("Beer sensor temperature: " + str(sensor_beer_value))
        print("Beer sensor temperature:", sensor_beer_value)
        logger.info("Average temperature: " + str(average_temp))
        print("Average temperature:", average_temp)
    
        if timestep == 60:
            timestep = 0
            if average_temp > DESIRED_TEMP + DELTA_OVERSHOOT_TEMP:
                if not GPIO.input(SSR_PIN):
                    logger.info("Turning on compressor")
                    print("Turning on compressor")
                    GPIO.output(SSR_PIN, True)
            if average_temp <= DESIRED_TEMP:
                if GPIO.input(SSR_PIN):
                    GPIO.output(SSR_PIN, False)
                    logger.info("Turning off compressor")
                    print("Turning off compressor")
        print("Timestep:", timestep, "of", 60)
        print("\n")
        sleep(READING_TICK)

except:
    GPIO.cleanup()
