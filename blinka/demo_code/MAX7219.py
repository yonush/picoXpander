"""
  MAX7219 display library
 
"""
import sys
import os
# required for the local libe folder - similar folder structure to CircuitPython and MicroPython
sys.path.insert(0, os.path.abspath('./lib'))

# download from https://circuitpython.org/libraries
import adafruit_max7219.matrices
from xpander import Xpander
from random import randint

PLC = Xpander()
PLC.setSPI() # enable the CS and busio

matrix = adafruit_max7219.matrices.CustomMatrix(PLC.SPI, PLC.SPI_CS, 8, 8)
matrix.brightness(3)
matrix.fill(False)

# display a random led
for i in range(10):
    matrix.clear_all()
    matrix.pixel(randint(0, 7), randint(0, 7), 1)
    matrix.show()