"""
  Testing the MAX7219 display library
  This code also works with Blinka a variation of https://github.com/adafruit/Adafruit_Blinka
 
  version 0.0.2
"""

import sys
import os

# required for the local lib folder - similar folder structure to CircuitPython and MicroPython
sys.path.insert(0, os.path.abspath("./lib"))

# downloaded from https://circuitpython.org/libraries
import adafruit_max7219.matrices
from xpander import Xpander
from random import randint

# create an instance of the Xpander class as the PLC
PLC = Xpander()
PLC.setSPI()  # enable the CS and busio

matrix = adafruit_max7219.matrices.CustomMatrix(PLC.SPI, PLC.SPI_CS, 8, 8)
matrix.brightness(3)
matrix.fill(False)

# display a random led
for i in range(10):
    matrix.clear_all()
    matrix.pixel(randint(0, 7), randint(0, 7), 1)
    matrix.show()
