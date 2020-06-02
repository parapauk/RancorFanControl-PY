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
logging.basicConfig(filename='/fan/fan.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT)

GPIO.output(16, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(16, GPIO.LOW)
time.sleep(0.2)
GPIO.output(16, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(16, GPIO.LOW)
time.sleep(0.2)
GPIO.output(16, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(16, GPIO.LOW)
time.sleep(0.2)
GPIO.output(16, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(16, GPIO.LOW)
time.sleep(0.2)
GPIO.output(16, GPIO.HIGH)
time.sleep(1)
GPIO.output(16, GPIO.LOW)
time.sleep(0.2)
brightness = GPIO.PWM(16, 100)
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

log = '/fan/log/log.log'
###
# Choose which fan preset
###
# ULTRA AGGRESIVE
###
#temp = '35'

###
# AGGRESIVE
###
temp = '45'

###
# RELAXED
###
#temp = '55'

###
# QUIET
###
#temp = '65'
###
###
# How quickly should it kick in? - The more tries, the longer the cpu has to remain at the target temp for the fans to kick in
###
# Immediately
###
#tries = 1
###
# Short
###
tries = 3
###
# Long
###
#tries = 7
###
# Very Long
###
#tries = 12
###
multi = 100 / (int(tries) + 2)
i = 0
try:
    while True:
        currentTemp = \
            subprocess.check_output('vcgencmd measure_temp | cut -c6,7'
                                    , shell=True)
        targetFilePath = '/sys/class/gpio/gpio2/value'
        targetFile = open(targetFilePath, 'w')
        fanStatusFile = 'status'
        fanStatus = open(fanStatusFile, 'w')
        brightness.start(0)
        brightnessLevel = 0
        if int(currentTemp) >= int(temp):
            i += 1
            if i > 1:
                brightnessLevel = (int(i) - 1) * int(multi)
            else:
                brightnessLevel = 0
            if int(brightnessLevel) > 99:
                brightnessLevel = 99
            brightness.ChangeDutyCycle(brightnessLevel)
            logging.debug('Temp exceeded ' + str(int(currentTemp)))
            if i > tries:
                targetFile.write('1')
                targetFile.close()
                fanStatus.write('on|' + str(int(currentTemp)))
                fanStatus.close()
                GPIO.output(16, GPIO.HIGH)
                #brightness.ChangeDutyCycle(100)
                logging.debug('Fan turned on ' + str(int(currentTemp)))
                i = int(i) - 1
        else:
            targetFile.write('0')
            targetFile.close()
            fanStatus.write('off|' + str(int(currentTemp)))
            fanStatus.close()
            GPIO.output(16, GPIO.LOW)
            logging.debug('Fan turned off ' + str(int(currentTemp)))
            i = 0
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Cancelled')
    logging.info('Script killed via keyboard')
