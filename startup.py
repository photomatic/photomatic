import RPi.GPIO as GPIO
import time
import os
import git

signalLed = 25
startSwitch = 4
updateSwitch = 27
repoPath = os.getenv('/home/pi/Documents/git_photomatic')

GPIO.setmode(GPIO.BCM)
GPIO.setup(startSwitch,GPIO.IN)
GPIO.setup(updateSwitch,GPIO.IN)
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
        
    if (GPIO.input(updateSwitch)):
        repo = git.Repo(repoPath)
        for remote in repo.remotes:
            remote.pull()
##        g = git.Git(photomatic.git)
##        g.pull()
            time.sleep(1)
        if (ledState == GPIO.HIGH):
            ledState = GPIO.LOW
            time.sleep(0.2)
        else:
            ledState = GPIO.HIGH
            time.sleep(0.2)
        done = True
        
ledState = GPIO.LOW
        
