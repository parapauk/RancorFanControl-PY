#!/usr/bin/python
# -*- coding: utf-8 -*-
# rancorFANcontrolPI-PY
#
# A simple python script I wrote to enable the Pi to control your fan(s) based on the temp of the CPU
#
#
# https://rancor.uk
#
#

import RPi.GPIO as GPIO
import time
import subprocess
import logging
import os
from pathlib import Path
logging.basicConfig(filename='/fan/fan.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


log = '/fan/log/log.log'
# target temp
temp = 46
# how many breaches of the temp before turning fan on? (higher = longer)
tries = 5
temp = int(temp) * 0.935
multi = 100 / (int(tries) + 2)
i = 0
off = 0
status = 'off'
targetFilePath = '/sys/class/gpio/gpio2/value'
fan = 2
led = 16





GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led, GPIO.OUT)

brightness = GPIO.PWM(led, 100)
brightness.start(0)
setup = '/sys/class/gpio/gpio2/direction'
try:
    with open(setup) as f:
        logging.info('Script has been killed manually and re-run')
except IOError:
    subprocess.check_output('echo "2">/sys/class/gpio/export',
                            shell=True)
    subprocess.check_output('echo "out">/sys/class/gpio/gpio2/direction'
                            , shell=True)
    logging.info('Script has been ran from cron automatically')

targetFilePath = '/sys/class/gpio/gpio2/value'
targetFile = open(targetFilePath, 'w')
targetFile.write('0')
targetFile.close()

try:
    while True:
        currentTemp = \
            subprocess.check_output('vcgencmd measure_temp | cut -c6,7'
                                    , shell=True)
        logging.debug('Iteration: ' + str(int(i)) + ' - Temp: ' + str(int(currentTemp)) + ' - Aiming for ' + str(int(temp)) + ' - Currently: ' + str(status) + ' - Off Counter: ' + str(int(off)))
        targetFilePath = '/sys/class/gpio/gpio2/value'
        targetFile = open(targetFilePath, 'w')
        fanStatusFile = 'status'
        fanStatus = open(fanStatusFile, 'w')
        #brightnessLevel = 0
        if int(currentTemp) >= int(temp):
            off = 0
            i += 1
            if i > 1:
                brightnessLevel = (int(i) - 1) * int(multi)
            else:
                brightnessLevel = 0
            if int(brightnessLevel) > 99:
                brightnessLevel = 99
            brightness.ChangeDutyCycle(brightnessLevel)
            logging.debug('Temp exceeded ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
            if i > tries:
                if status == 'off':
                    status = 'on'
                    targetFile.write('1')
                    targetFile.close()
                    fanStatus.write('on|' + str(int(currentTemp)))
                    fanStatus.close()
                    brightness.ChangeDutyCycle(100)
                    #brightness.ChangeDutyCycle(100)
                    logging.debug('Fan TURNED ON ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                else:
                    logging.debug('Fan ALREADY ON ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                i = int(i) - 1
        else:
            if status == 'on':
                off += 1
                if off >= tries:
                    #time.sleep(int(tries) * 5)
                    targetFile.write('0')
                    targetFile.close()
                    fanStatus.write('off|' + str(int(currentTemp)))
                    fanStatus.close()
                    #GPIO.output(16, GPIO.LOW)
                    brightness.ChangeDutyCycle(0)
                    logging.debug('Fan TURNED OFF ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                    off = 0
                    status = 'off'
                    i = 0
                else:
                    logging.debug('Preparing to TURN OFF. ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                    i = int(i) - 1
            else:
                logging.debug('Nothing to do. Iteration: ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                off = 0
                if i > 0:
                    i = int(i) - 1
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Cancelled')
    logging.info('Script killed via keyboard')

