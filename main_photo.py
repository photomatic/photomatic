#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################
# IMPORTATION DES PACKAGES

from PIL import Image
import subprocess
##
from subprocess import check_output, CalledProcessError
import time
from time import gmtime, strftime, sleep
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

#import physicalUI
#import Reference as r

#######################################
# FONCTIONS

#Callback du switch run
#def runCallback


# Callback du bouton déclencheur
def buttonCallback(channel):
    global photomaticState
    print("Bouton pressé")
    photomaticState = "takePicture"

# Permet de monter le device USB si ce n'est pas le cas. Retrourne le chemin de la partition.
def get_mount_points(devices=None):
    '''
    Cherche si un disque dur est connecté, crée un dossier "photomatic". Fait clignoter la led auxiliaire si un disque n'est pas connecté.
    :return: renvoie le chmemin vers lequel enregistrer les fichiers
    '''
    
##    context = pyudev.Context()
##
##    removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
##    for device in removable:
##        partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
##        print("All removable partitions: {}".format(", ".join(partitions)))
##        print("Mounted removable partitions:")
    for p in psutil.disk_partitions():
            #if p.device in partitions:
        print("  {}: {}".format(p.device, p.mountpoint))



# Commande de l'appareil photo et chargement de l'image sur le pi
def cameraShutter():
    '''
    Déclenche la caméra et télécharge l'image sur le raspberry (voir sur le disque dur)
    :return: le chemin vers la photo qui vient d'être prise
    '''
    imageName = "photomatic_"+ strftime("%Y-%m-%d_%H%M%S",gmtime()) + ".jpg"
    imageFilePath = FOLDER_PHOTOS + imageName
    gpout=""
    
    try:
        gpout = subprocess.check_output("gphoto2 --capture-image-and-download --keep-raw --filename " + imageFilePath, stderr=subprocess.STDOUT, shell=True)
        
        if 'ERROR' in gpout:
            print (gpout)
            logging.error(gpout)
            raise IOError("La commande a échoué au niveau de Gphoto pour la photo:" + imageFilePath)
	
    except subprocess.CalledProcessError as e:
        logging.error("La photo ne peut pas être prise. La caméra est probablement en cause")
        logging.error(e)
        raise
		
    except Exception as e:
        logging.error("La commande a échoué au niveau d'une exception générale pour cette photo:" + imageFilePath)
        logging.error(e)
        raise
    else:
        return imageFilePath
    
# Fait pulser les leds de l'avant du photomaton    
def ledPulse():
    for x in range (0,100,1):
        ledPWM.ChangeDutyCycle(x)
        time.sleep(0.005)
    for x in range (100,0,-1):
        ledPWM.ChangeDutyCycle(x)
        time.sleep(0.005)
        
# Envoie les LEDs à fond les ballons 
def ledFull():
    ledPWM.ChangeDutyCycle(100)
    
# Eteint les LEDs    
def ledOff():
    ledPWM.ChangeDutyCycle(0)

# LEDs a 20%
def ledIdle():
    ledPWM.ChangeDutyCycle(20)
    
# Permet d'obtenir un chemin aléatoire pour le diaporama aléatoire
def randomFileName(dir):
    """
    Prend le chemin des photos en argument et retourne un de photo aléatoire à afficher.
    """
    files = [os.path.join(path,filename)
    	for path,dirs,files in os.walk(dir)
            for filename in files]
    randomPath = random.choice(files)
    print(randomPath)
    return randomPath

# Affiche la photo sur l'écran
def displayPicture(pictureFilePath,displayTime):
    """ 
    Affiche la photo qui vient d'être prise en prenant le chemin de celle-ci 
    en argument ainsi que le temps qu'elle doit s'afficher.
    """
    screen.fill((0,0,0))
    
    img = pygame.image.load(pictureFilePath)
    img = pygame.transform.scale(img,(w,h))
    screen.blit(img,(0,0))
    pygame.display.flip()
    time.sleep(displayTime)
	
# Affiche du texte
def displayText(textToPrint,blackScreen):
    """
    Fonction permettant d'afficher le texte passé en argument sur l'écran.
    Voir pour éventuellement rajouter des paramètres de texte (couleur, taille, etc).
    """
    if blackScreen == True:
        screen.fill((0,0,0))
        
    font = pygame.font.SysFont("Helvetica",48)
    text = font.render(textToPrint,True,(255,255,255))
	
    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    textrect.centery = screen.get_rect().centery
    
    screen.blit(text,textrect)
    
    pygame.display.flip()

# Permet d'afficher un diaporama	
def diaporama():
    """
    Permet de passer un diaporama  des différentes image qui ont déjà été prises.
    La fonction prend le temps d'affichage de chaque image en argument.
    """
    while True:
        if diaporamaRunning == True:
            print("Diaporama Running")
##            displayText("Diaporama des photos précédentes",False)
            displayPicture(randomFileName(FOLDER_PHOTOS), diaporamaTime)
            
    
# Fonction générale pour prendre la photo et l'afficher, le tout avec du texte
def takePicture():
    """
    Permet d'activer le shutter de la camera, garder un RAW, 
    charger le jpeg et l'afficher. Le tout est expliqué à l'utilisateur 
    par des messages sur l'écran.
    """
	
    photoPath = ""

    try:
        photoPath = cameraShutter()

    except subprocess.CalledProcessError:
        #physicalUI.ledEvent()
        print ("Unable to take photo as camera is not turned on, out of focus or battery is dead")
        logging.error("Unable to take photo as camera is not turned on, out of focus or battery is dead")
        raise Exception("Camera is not responding, battery is dead, out of focus or camera is not turned on")

    else:
        return photoPath
        

def photoCycle():
    """
    La fonction contient tout le cycle nécessaire pour prendre une photo.
    Contient les info PhysicalUI, gestion camera, affichage et texte.
    """
    processSuccess = False
    photoPathOriginal = ""
    
    # Display Text
    displayText("Attention! Souriez!", True)
    time.sleep(1)
    displayText("3", True)
    ledPulse()
    displayText("2", True)
    ledPulse()
    displayText("1", True)
    ledPulse()
    displayText("Clic Clac!", True)
    ledFull()
    # Take the picture
    photoPathOriginal = takePicture()
    ledIdle()
    displayPicture(photoPathOriginal,5)
##    displayText("Photo prise!",False)
    
    # rajouter touts les infos physical UI, Diaporama et texte
    
    processSuccess = True

def imageBlend(photoPath,logoPath):

    image = Image.open(photoPath)
    imageSize =image.size
    logo = Image.open(logoPath)
    logoSize = logo.size
    
    #Positionne le logo en bas à droite. A réfléchir si on fait plusieurs cas de figure à hardcoder ou si on fait un dialogbox pour pouvoir changer ça facilement.
    logoPositionX = imageSize[1]-logoSize[1]
    logoPositionY = imageSize[2]-logoSize[2]
    
    commandOverlay = 'usr/bin/convert' + photoPath + logoPath +'-geometry'+ logoPositionX + logoPositionY +'-composite' + photoPath
    call([commandOverlay],shell=True)
    
    
def checkKeyboardEvent():
    global keyPressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type is pygame.KEYDOWN and event.key == pygame.K_ESCAPE ):
            pygame.quit()
            sys.exit
    
	
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
PIN_PWM_LED = int(18)
PIN_LED = int(25)
PIN_OUT1 = int(23)
PIN_OUT2 = int(24)

#Photo path
FOLDER_PHOTOS = "/media/pi/BROWNIE/Original/"


#*****************Screen Settings*************
pygame.init()
pygame.mouse.set_visible(False)
##w = pygame.display.Info().current_w
##h = pygame.display.Info().current_h
w = 1024
h = 768
screenSize = (w,h)
screen = pygame.display.set_mode(screenSize) #,pygame.FULLSCREEN)

#*****************Logging Settings*************
logging.basicConfig(filename="photomaticLog.txt",
                    level=logging.DEBUG,
                    format='%(levelname)s: %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

logging.info("Le programme Photomatic est lancé!")

#*****************GPIO Settings*************
GPIO.setmode(GPIO.BCM)

#Pressbutton
GPIO.setup(PIN_SWITCH_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(PIN_SWITCH_IN,GPIO.FALLING, callback=buttonCallback, bouncetime = 200)

#LED PWM
GPIO.setup(PIN_PWM_LED, GPIO.OUT)
ledPWM = GPIO.PWM(PIN_PWM_LED,100)
ledPWM.start(0)
ledIdle()

#Switch Run

##GPIO.setup(PIN_RUN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
##GPIO.add_event_detect(PIN_RUN,GPIO.FALLING, callback=runCallback, bouncetime = 200)

#LED Out
GPIO.setup(PIN_LED, GPIO.OUT)

#Main Loop
photomaticState = "idle"

diaporamaRunning = False


diapoThread = Thread(target=diaporama)
diapoThread.start()

try:
    DRIVE = get_mount_points()
except Exception as e:
    logging.error("Problème de connexion du disque dur")
    logging.error(e)
else:
    logging.debug("Disque dur connecté et chemin de fichier transmis")            
            
DRIVE = get_mount_points()
#print get_mount_points()


try:
    while True:
        # Check Keyboard Event
        checkKeyboardEvent()
        
        if photomaticState == "idle":
            diaporamaRunning = True
        elif photomaticState == "takePicture":
            diaporamaRunning = False
            try:
                photoCycle()
                
            except Exception as e:
                logging.error("Problème dans la fonction photocycle")
                logging.error(e)
                #Indiquer l'erreur avec un pattern de LEDs
                
            else:
                logging.debug("Une photo a été prise avec succès")
                
            photomaticState = "idle"
            
            
        

                
except KeyboardInterrupt:
    print ("Le process a été arrêté au moyen du clavier")
    #Eteindre toutes les LEDs avec un signe distinctif
    logging.debug("Le programme a été arrêté au moyen du clavier")
    GPIO.cleanup()
