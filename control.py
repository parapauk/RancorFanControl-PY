#!/usr/bin/python
# -*- coding: utf-8 -*-
# rancorFANcontrol-PI
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
logging.basicConfig(filename='/fan/fan.log', level=logging.INFO,
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

pidfile = '/fan/fan.pid'
setup = '/sys/class/gpio/gpio2/direction'
try:
    with open(setup) as f:
        logging.warning('Script has been killed manually and re-run')
except IOError:
    subprocess.check_output('echo "2">/sys/class/gpio/export',
                            shell=True)
    subprocess.check_output('echo "out">/sys/class/gpio/gpio2/direction'
                            , shell=True)
    logging.warning('Script has been ran from cron automatically')

log = '/fan/log/log.log'
temp = '50'

try:
    while True:
        currentTemp = \
            subprocess.check_output('vcgencmd measure_temp | cut -c6,7'
                                    , shell=True)
        targetFilePath = '/sys/class/gpio/gpio2/value'
        targetFile = open(targetFilePath, 'w')
        if int(currentTemp) > int(temp):
            targetFile.write('1')
            GPIO.output(16, GPIO.HIGH)
            logging.info('Fan turned on ' + str(int(currentTemp)))
        else:
            targetFile.write('0')
            GPIO.output(16, GPIO.LOW)
            logging.info('Fan turned off ' + str(int(currentTemp)))
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Cancelled')

