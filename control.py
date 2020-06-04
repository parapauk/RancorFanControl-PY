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

from gpiozero import PWMLED
import time, subprocess, logging, os, threading
from datetime import datetime
from pathlib import Path
logging.basicConfig(filename='/fan/fan.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# csv location
csv = '/fan/temps.csv'
# target temp
temp = 46
# how many breaches of the temp before turning fan on? (higher = longer)
tries = 12
# multiplier to compensate for minor temp adjustments
temp = int(temp) * 0.935
# fan gpio number (un-used)
fan = 2
# led gpio number (un-used)
led = 16
# led gpio number
newLed = PWMLED(16)


######################################
# DONT EDIT BELOW HERE!!
######################################

multi = 100 / (int(tries))
i = 0
off = 0
status = 'off'
targetFilePath = '/sys/class/gpio/gpio2/value'

def blinkenLighten():
    newLed.pulse()
    time.sleep(20)


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
thread = threading.Thread(target=blinkenLighten)
try:
    while True:
        currentTemp = \
            subprocess.check_output('vcgencmd measure_temp | cut -c6,7'
                                    , shell=True)
        tempLog = open(csv,"a")
        tempLog.write(str(datetime.now()) + ',' + str(int(currentTemp)) + ',' + str(int(temp)) + ',' + str(status) + ',' + str(int(tries)) + '\n')
        tempLog.close()
        logging.debug('Iteration: ' + str(int(i)) + ' - Temp: ' + str(int(currentTemp)) + ' - Aiming for ' + str(int(temp)) + ' - Currently: ' + str(status) + ' - Off Counter: ' + str(int(off)))
        targetFilePath = '/sys/class/gpio/gpio2/value'
        targetFile = open(targetFilePath, 'w')
        fanStatusFile = 'status'
        fanStatus = open(fanStatusFile, 'w')
        #brightnessLevel = 0
        if int(currentTemp) > int(temp):
            off = 0
            i += 1
            if i > 1:
                brightnessLevel = ((int(i) - 1) * int(multi) / 100)
            else:
                brightnessLevel = 0
            if int(brightnessLevel) > 1:
                brightnessLevel = 1
            #print(brightnessLevel)
            newLed.value = brightnessLevel
            logging.debug('Temp exceeded ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)) + ' - Brightness: ' + str(int(brightnessLevel)))
            if i > tries:
                if status == 'off':
                    status = 'on'
                    targetFile.write('1')
                    targetFile.close()
                    fanStatus.write('on|' + str(int(currentTemp)))
                    fanStatus.close()
                    #brightness.ChangeDutyCycle(100)
                    #brightness.ChangeDutyCycle(100)
                    #newLed.on()
                    thread = threading.Thread(target=blinkenLighten)
                    thread.start()
                    logging.debug('Fan TURNED ON ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                else:
                    logging.debug('Fan ALREADY ON ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                i = int(i) - 1
        else:
            if status == 'on':
                off += 1
                if off > (tries):
                    #time.sleep(int(tries) * 5)
                    newLed.pulse()
                    targetFile.write('0')
                    targetFile.close()
                    fanStatus.write('off|' + str(int(currentTemp)))
                    fanStatus.close()
                    #GPIO.output(16, GPIO.LOW)
                    #brightness.ChangeDutyCycle(0)
                    time.sleep(2)
                    newLed.off()
                    logging.debug('Fan TURNED OFF ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                    off = 0
                    status = 'off'
                    i = 0
                else:
                    #brightnessLevel = ((int(tries) - off) / 100)
                    #newLed.value = brightnessLevel
                    logging.debug('Preparing to TURN OFF. ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                    if i < 1:
                        i = 0
                    else:
                        i = int(i) - 1
            else:
                logging.debug('Nothing to do. Iteration: ' + str(int(currentTemp)) + ' - aiming for ' + str(int(temp)))
                off = 0
                if i < 1:
                    i = 0
                else:
                    i = int(i) - 1
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Cancelled')
    logging.info('Script killed via keyboard')

