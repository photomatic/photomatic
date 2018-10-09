
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8


#######################################
######### Module photomatic ###########

# Custom Photomatic functions. Should be imported as a package in the main file.
# Author: Jonathan Braun 2018

########################################################################################################################

# Permet de monter le device USB si ce n'est pas le cas. Retourne le chemin de la partition.

def get_mount_points(devices=None):
    '''
    Cherche si un disque dur est connecté, crée un dossier "photomatic". Fait clignoter la led auxiliaire si un disque n'est pas connecté.
    :return: renvoie le chmemin vers lequel enregistrer les fichiers
    '''

    for p in psutil.disk_partitions():
            #if p.device in partitions:
        print("  {}: {}".format(p.device, p.mountpoint))

    return "{}".format(p.device)


########################################################################################################################

#TODO: Clean this function and create a coherent log and error handling system

# Commande de l'appareil photo et chargement de l'image sur le pi

def cameraShutter():
    '''
    Déclenche la caméra et télécharge l'image sur le raspberry (voir sur le disque dur)
    :return: le chemin vers la photo qui vient d'être prise
    '''
    imageName = "photomatic_" + strftime("%Y-%m-%d_%H%M%S", gmtime()) + ".jpg"
    imageFilePath = FOLDER_PHOTOS + imageName
    gpout = ""

    try:
        gpout = subprocess.check_output("gphoto2 --capture-image-and-download --keep-raw --filename " + imageFilePath,
                                        stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        displayText("Photo prise!", False)
        if 'ERROR' in gpout:
            print(gpout)
            logging.error(gpout)
            print("La commande a échoué au niveau de Gphoto pour la photo:" + imageFilePath)
            raise IOError("La commande a échoué au niveau de Gphoto pour la photo:" + imageFilePath)

    except subprocess.CalledProcessError as e:
        print("La photo ne peut pas être prise. La caméra est probablement en cause")
        print(e)
        logging.error("La photo ne peut pas être prise. La caméra est probablement en cause")
        logging.error(e)
        raise

    except Exception as e:
        print(e)
        print("Exception")
        logging.error("La commande a échoué au niveau d'une exception générale pour cette photo:" + imageFilePath)
        logging.error(e)
        raise
    else:
        print("Nouvelle Photo:")
        print(imageFilePath)
        return imageFilePath


# Fonction générale pour prendre la photo et l'afficher, le tout avec du texte
def takePicture(lastPicTime):
    """
    Permet d'activer le shutter de la camera, garder un RAW,
    charger le jpeg et l'afficher. Le tout est expliqué à l'utilisateur
    par des messages sur l'écran.
    """
    processSuccess = False
    photoPath = ""

    # Display Text
    displayText("La photo va être prise!", True)
    ledPulse(0.003)
    displayText("", True)
    ledPulse(0.3)
    ledPulse(0.1)
    ledFull()

    # Take the picture
    try:
        photoPath = cameraShutter()

    except subprocess.CalledProcessError:
        ledOff()
        print("Unable to take photo as camera is not turned on, out of focus or battery is dead")
        logging.error("Unable to take photo as camera is not turned on, out of focus or battery is dead")
        raise Exception("Camera is not responding, battery is dead, out of focus or camera is not turned on")

    else:
        ledOff()
        displayPicture(photoPath, lastPicTime)
        print("Picture taken:")
        print(photoPath)
        processSuccess = True

########################################################################################################################

# def photoCycle(lastPicTime):
#     """
#     La fonction contient tout le cycle nécessaire pour prendre une photo.
#     Contient les info PhysicalUI, gestion camera, affichage et texte.
#     """
#     processSuccess = False
#     photoPathOriginal = ""
#
#     # Display Text
#     displayText("La photo va être prise!", True)
#     ledPulse(0.003)
#     displayText("", True)
#     ledPulse(0.3)
#     ledPulse(0.1)
#     ledFull()
#     # Take the picture
#     photoPathOriginal = takePicture()
#
#     print(photoPathOriginal)
#     ledOff()
#     displayPicture(photoPathOriginal, lastPicTime)
#
#     processSuccess = True

########################################################################################################################

# Fait pulser les leds de l'avant du photomaton

def ledPulse(speed):
    for x in range (0,5,1):
        GPIO.output(PIN_PWM_LED,GPIO.LOW)
        time.sleep(speed)
        GPIO.output(PIN_PWM_LED,GPIO.HIGH)
        time.sleep(speed)

# Envoie les LEDs à fond les ballons

def ledFull():
    GPIO.output(PIN_PWM_LED,GPIO.LOW)

# Eteint les LEDs

def ledOff():
    GPIO.output(PIN_PWM_LED,GPIO.HIGH)

# LEDs a 20%  Seulement implémenté lorsque le contrôle sera à base de MOSFET...Pour l'instant relais

def ledIdle():
    GPIO.output(PIN_PWM_LED,GPIO.HIGH)

########################################################################################################################

# Permet d'obtenir un chemin aléatoire pour le diaporama

def randomFileName(dir):
    """
    Prend le chemin des photos en argument et retourne un de photo aléatoire à afficher.
    """
    files = [os.path.join(path, filename)
             for path, dirs, files in os.walk(dir)
             for filename in files]
    randomPath = random.choice(files)
    print(randomPath)
    return randomPath

########################################################################################################################

# Scale l'image en fonction de la résolution de l'écran

def aspectScale(img, bx, by):
    ix, iy = img.get_size()
    if ix > iy:
        scale_factor = bx / float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by / float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        scale_factor = by / float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx / float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    sx = int(sx)
    sy = int(sy)
    return sx, sy

########################################################################################################################

# Affiche du texte

def displayText(textToPrint, blackScreen):
    """
    Fonction permettant d'afficher le texte passé en argument sur l'écran.
    Voir pour éventuellement rajouter des paramètres de texte (couleur, taille, etc).
    """
    if blackScreen == True:
        screen.fill((0, 0, 0))

    font = pygame.font.SysFont("Helvetica", 48)
    text = font.render(textToPrint, True, (255, 255, 255))

    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    textrect.centery = screen.get_rect().centery

    screen.blit(text, textrect)

    pygame.display.flip()

########################################################################################################################

# Affiche la photo sur l'écran

def displayPicture(pictureFilePath, displayTime):
    """
    Affiche la photo qui vient d'être prise en prenant le chemin de celle-ci
    en argument ainsi que le temps qu'elle doit s'afficher.
    """
    screen.fill((0, 0, 0))
    img = pygame.image.load(pictureFilePath)
    sx, sy = aspectScale(img, w, h)
    img = pygame.transform.scale(img, (sx, sy))
    imgRect = img.get_rect(center=screen.get_rect().center)
    screen.blit(img, imgRect)
    pygame.display.flip()
    time.sleep(displayTime)

########################################################################################################################

# Permet d'afficher un diaporama

def diaporama():
    """
    Permet de passer un diaporama  des différentes image qui ont déjà été prises.
    La fonction prend le temps d'affichage de chaque image en argument.
    """
    while not done:
        if diaporamaRunning == True:
            print("Diaporama Running")
            ##            displayText("Diaporama des photos précédentes",False)
            displayPicture(randomFileName(FOLDER_PHOTOS), diaporamaTime)

########################################################################################################################

# TODO: Implémenter et tester la fonction. Pas utilisable pour le moment.
# # Fonction de blend d'image avec un logo en png
# def imageBlend(photoPath, logoPath):
#     image = Image.open(photoPath)
#     imageSize = image.size
#     logo = Image.open(logoPath)
#     logoSize = logo.size
#
#     # Positionne le logo en bas à droite. A réfléchir si on fait plusieurs cas de figure à hardcoder ou si on fait un dialogbox pour pouvoir changer ça facilement.
#     logoPositionX = imageSize[1] - logoSize[1]
#     logoPositionY = imageSize[2] - logoSize[2]
#
#     commandOverlay = 'usr/bin/convert' + photoPath + logoPath + '-geometry' + logoPositionX + logoPositionY + '-composite' + photoPath
#     call([commandOverlay], shell=True)

########################################################################################################################

# Fonction de polling et d'envoi sur la galerie internet

def sendToGallery():
    oldFiles = dict([(f, None) for f in os.listdir(FOLDER_PHOTOS)])
    while (1):
        time.sleep(5)
        newFiles = dict([(f, None) for f in os.listdir(FOLDER_PHOTOS)])
        addedFiles = [f for f in newFiles if not f in oldFiles]
        if addedFiles:
            print(''.join(addedFiles))
            fileToLoad = FOLDER_PHOTOS + ''.join(addedFiles)
            print(fileToLoad)
            uploadFile(fileToLoad)
        oldFiles = newFiles

########################################################################################################################

# Fonction d'upload du fichier sur internet

def uploadFile(filename):
    try:
        if (os.path.isfile(filename)):
            files = {'phpGallery_images': open(filename, 'rb')}
            r = requests.post(galleryURL, files=files, timeout=60)
            print(r)
        else:
            print('Failed with path')
    except:
        print('Upload failed.')

########################################################################################################################

# Splashscreen du photomaton

def photomaticIntro():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    screen.fill((255, 255, 255))
    largetext = pygame.font.SysFont("Helvetica", 60)
    smalltext = pygame.font.SysFont("Helvetica", 30)
    text = largetext.render("Photomatic 2.0", True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery
    screen.blit(text, textRect)
    text = smalltext.render("J. Braun | R. Huck | 2018", True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = (screen.get_rect().centery) + 100
    screen.blit(text, textRect)
    text = largetext.render("Prenez une photo pour commencer!", True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = (screen.get_rect().centery) + 200
    screen.blit(text, textRect)
    pygame.display.update()

########################################################################################################################

# TODO: Eventuellement implémenter la possibilité de faire un toggle du fullscreen. A définir si c'est vraiment nécessaire
# def checkScreenCallback(channel):

#    if (fullScreen == True):
#        fullScreen != fullScreen
###        pygame.display.quit()
###        pygame.display.init()
###        w = pygame.display.Info().current_w
###        h = pygame.display.Info().current_h
#        screenSize = (w,h)
#        screen = pygame.display.set_mode(screenSize,pygame.FULLSCREEN) #,pygame.FULLSCREEN)
#    else:
#        fullScreen != fullScreen
###        pygame.display.quit()
###        pygame.display.init()
###        w = pygame.display.Info().current_w
###        h = pygame.display.Info().current_h
#        screenSize = (w,h)
#        screen = pygame.display.set_mode(screenSize)