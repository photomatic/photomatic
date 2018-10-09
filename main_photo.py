#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8


########## PHOTOMATIC #################
# Main file for the photomatic connected photobooth
# Author: Jonathan Braun 2018
#######################################
# IMPORTATION DES PACKAGES

from PIL import Image
import subprocess
##
from subprocess import check_output, CalledProcessError
import time
from time import gmtime, strftime #, sleep
import logging
import RPi.GPIO as GPIO
import os
import pygame
import random
import sys
from threading import Thread
##
from glob import glob 
import pyudev
import psutil
import os.path

try:
  import requests
except ImportError:
  print "Trying to Install required module: requests\n"
  os.system('python -m pip install requests')
  import requests
# -- above lines try to install requests module if not present
# -- if all went well, import required module again ( for global access)

import photomatic

global done
global diaporamaRunning
global w
global h
global fullScreen
global screen
global galleryURL

done = False
diaporamaRunning = False
w = 1024
h = 768
fullScreen = False
galleryURL = 'XXX URL XXX'
#######################################
# Callbacks and specific functions


# Callback du bouton déclencheur

def buttonCallback(channel):
    global photomaticState
    print("Bouton pressé")
    photomaticState = "takePicture"

    
#######################################################################################################################
########################################## Main #######################################################################

# TODOS
# TODO: Implémenter la possibilité de lire le code du wifi depuis un wfichier texte ou de le demander directement via un prompt.

# Main instructions for the photomatic loop

#***************** Program Settings  *************
diaporamaTime = int(3)
lastPicTime = int(5)

#***************** IO Settings  *************

#Inputs
PIN_SWITCH_IN = int(13)
PIN_RUN = int(4)
PIN_OVERLAY = int(27)
PIN_IN1 = int(26)
PIN_SW3 = int(5)
PIN_SW4 = int(17)
PIN_SW5 = int(22)
PIN_SW6 = int(6)

#Outputs
PIN_PWM_LED = int(24)
PIN_LED = int(25)
PIN_OUT1 = int(23)
#PIN_OUT2 = int(24)

#***************** GPIO Settings *************

GPIO.setmode(GPIO.BCM)

#Pressbutton
GPIO.setup(PIN_SWITCH_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(PIN_SWITCH_IN,GPIO.FALLING, callback=buttonCallback, bouncetime = 200)
GPIO.setup(PIN_SW3, GPIO.IN)  # Switch for the activation of the upload or not

#LED Relay
GPIO.setup(PIN_PWM_LED,GPIO.OUT)
GPIO.output(PIN_PWM_LED,GPIO.HIGH)
ledIdle()

#Switch
##GPIO.setup(PIN_SW3,GPIO.IN)
##GPIO.add_event_detect(PIN_SW3,GPIO.BOTH)
##GPIO.add_event_callback(PIN_SW3,checkScreenCallback)
##GPIO.setup(PIN_RUN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
##GPIO.add_event_detect(PIN_RUN,GPIO.FALLING, callback=runCallback, bouncetime = 200)

#LED Out
GPIO.setup(PIN_LED, GPIO.OUT)

#***********************************************
#Photo path

FOLDER_PHOTOS = "/media/pi/PHOTOMATIC4/Original/"

#***************** Screen Settings *************

pygame.init()
pygame.mouse.set_visible(False)
w = pygame.display.Info().current_w
h = pygame.display.Info().current_h
screenSize = (w,h)
screen = pygame.display.set_mode(screenSize,pygame.FULLSCREEN)

#***************** Logging Settings *************

logging.basicConfig(filename="photomaticLog.txt",
                    level=logging.DEBUG,
                    format='%(levelname)s: %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

logging.info("Le programme Photomatic est lancé!")

#######################################################################################################################
#***************** Main Loop *******************************************************************************************


########################### STARTUP #############################
photomaticState = "startup"



#TODO: Peut-être ajouter la possibilité de désactiver le diaporama avec un des switchs

# Start diaporama thread

diapoThread = Thread(target=diaporama)
#diapoThread.daemon = True
diapoThread.start()

# Start the upload thread if the switch is selected

if (GPIO.input(PIN_SW3)):
    uploadThread = Thread(target=sendToGallery)
    uploadThread = start()


# Find the drive mounting point

try:
    DRIVE = get_mount_points()
except Exception as e:
    logging.error("Problème de connexion du disque dur")
    logging.error(e)
else:
    logging.debug("Disque dur connecté et chemin de fichier transmis")            

FOLDER_PHOTOS = DRIVE + '/Original'
print(FOLDER_PHOTOS)

# Splashscreen

photomaticIntro()


########################### LOOP #############################

try:
    while not done:

        # Check keyboard event to quit the programm

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.QUIT:
                done = True
                pygame.quit()
                sys.exit()
        
        # Main State Machine
        if photomaticState == "startup":
            diaporamaRunning = False
        elif photomaticState == "idle":
            diaporamaRunning = True
        elif photomaticState == "takePicture":
            diaporamaRunning = False
            try:
                takePicture(lastPicTime)
                
            except Exception as e:
                logging.error("Problème dans la fonction photocycle")
                logging.error(e)
            else:
                logging.debug("Une photo a été prise avec succès")

            #TODO: Implémenter un driver de LED au niveau hardware et pouvoir les varier plutôt que les relais.
            ledIdle()
            photomaticState = "idle"


                
except KeyboardInterrupt:
    print ("Le process a été arrêté au moyen du clavier")
    done = True
    diapoThread.join()
    logging.debug("Le programme a été arrêté au moyen du clavier")
    GPIO.cleanup()
