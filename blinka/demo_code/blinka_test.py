"""
    picoXpander Blinka diagnostics test
    version 0.0.1    

"""
import os
import time

import hid
import serial.tools.list_ports as lp
from adafruit_platformdetect import Detector

# this environmental variable must be set, either in the code or from a terminal
#  otherwise the U2IF device will not be detected
print("Checking if system is ready for Blinka on the picoXpander")
print("Setting the environment variable BLINKA_U2IF, assuming it is not set in the OS\n")
os.environ["BLINKA_U2IF"] = "1"

#import board
#import digitalio

try:
	import board as board
	import digitalio as digitalio
except:
    print("ERR: No Raspberry Pico with U2IF firmware attached")
#    exit()



# check the USB
hid.enumerate()
v = 'device' in dir(hid)
if not v:
    print("ERR: HID support missing - try install hidapi and not hid")
else:    
    print(f"USB HID capable: {v}")

# check for com/serial ports
print(f"Serials ports")
for s in lp.comports():
    print(f"- {s.description}")

# check the Pico USB support
v = "No Pico found"
error = True
for d in hid.enumerate():
    if d["manufacturer_string"] == 'Pico':
       v = f"Pico attached {d["serial_number"]}" 
       error = False
       break
if error:    
    print("ERR: Pico with USB support missing")

# check the Pico has U2IF support
try:
    detector = Detector()
    print("Chip id: ", detector.chip.id)
    print("Board id: ", detector.board.id)
    if detector.board.id != "PICO_U2IF":
        print("ERR: Pico U2IF support missing - try installing the correct U2IF firmware")
except:
    print("ERR: Cannot detect a suitable Pico with U2IF firmware")

if not error:    
    device = hid.device()
    device.open(0xCAFE, 0x4005)
    print(f"Pico attached ({v})")
    device.close()
else:
    print("ERR: No suitable Pico attached with U2IF installed")

#check the environment variable
v = os.environ['BLINKA_U2IF']
if not v:
    print("ERR: Environment variable not set")
else:        
    print(f"Env. variable BLINKA_U2IF = {v}")

print("Checking board capabilities")
if error:
    print("Pico Installation issues")
    exit()

print(dir(board))
if not '__blinka__' in dir(board):
    print("Firmware capability issues")
    exit()

# do the Blinking thing
print("Time to blink an LED on GPIO14 & GPIO15")
led = digitalio.DigitalInOut(board.GP14)
led.direction = digitalio.Direction.OUTPUT

led2 = digitalio.DigitalInOut(board.GP15)
led2.direction = digitalio.Direction.OUTPUT

for  v in range(20):
    led.value = not led.value
    time.sleep(0.1)
    led2.value = not led2.value

led.value = False
led2.value = False    