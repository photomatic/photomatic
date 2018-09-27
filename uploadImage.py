#!/usr/bin/env python

import time
import os.path
import requests




galleryURL = 'http://romainhuck.com/upload.php'


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



oldFiles = dict([(f, None) for f in os.listdir('photos')])
while(1):
    time.sleep(5)
    newFiles = dict([(f,None) for f in os.listdir('photos')])
    addedFiles = [f for f in newFiles if not f in oldFiles]
    if addedFiles:
        print(''.join(addedFiles))
        fileToLoad = 'photos/' + ''.join(addedFiles)
        print(fileToLoad)
        uploadFile(fileToLoad)
    oldFiles = newFiles

