"""
    Demo testing the WS281b or neopixel leds.
    Up to 16 GRB leds are supported
"""
from xpander import Xpander
import time

PLC = Xpander()

# show an array of red leds in different intensities
buffer = [10] * 48
# white
PLC.RGBon(buffer)
time.sleep(1)
PLC.RGBoff()

# All green
c = 1
for i in range(0,48,3):
    buffer[i] = c
    buffer[i+1] = 0
    buffer[i+2] = 0
    c +=1       
PLC.RGBon(buffer)
time.sleep(1)
PLC.RGBoff()

# All red
c = 0
for i in range(0,48,3):
    buffer[i] = 0
    buffer[i+1] = c
    buffer[i+2] = 0       
    c +=1       
PLC.RGBon(buffer)
time.sleep(1)
PLC.RGBoff()

# All blue
c = 0
for i in range(0,48,3):
    buffer[i] = 0
    buffer[i+1] = 0
    buffer[i+2] = c       
    c +=1       
PLC.RGBon(buffer)
time.sleep(1)

# all off
PLC.RGBoff()