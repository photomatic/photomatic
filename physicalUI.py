#!/usr/bin/python

'''
Physical User Interface
Contains all the functions using GPIOs.
This includes interface buttons, LEDs etc. 
'''


from subprocess import call
import RPi.GPIO as GPIO
import time
import os.path

import Reference as r

def ledEvent(ledPinNumber):
	"""
	LEDs are flashing for an event in a specific pattern that means everything is OK
	"""

def ledFlashRapidly(ledPinNumber):
	"""
	Makes the LEDs flash rapidly before a picture is taken
	"""
	

def ledIdle(ledPinNumber):
	""" 
	Lights the LEDs in an idle level of light
	"""
	
	