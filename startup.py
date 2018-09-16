import RPi.GPIO as GPIO
import time
import os

signalLed = 25
startSwitch = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(startSwitch,GPIO.IN)
GPIO.setup(signalLed,GPIO.OUT)

done = False
ledState = GPIO.HIGH
while not done:
    time.sleep(1)
    if (ledState == GPIO.HIGH):
        ledState = GPIO.LOW
    else:
        ledState = GPIO.HIGH
        
    GPIO.output(signalLed,ledState)
    if (GPIO.input(startSwitch)):
        os.system("python3 -u /home/pi/Documents/git_photomatic/main_photo.py")
        done = True
        
ledState = GPIO.LOW
        
