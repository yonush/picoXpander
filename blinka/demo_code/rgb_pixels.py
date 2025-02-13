"""
    Demo testing the WS2812b or neopixel leds.
    Up to 16 GRB leds are supported

    This code also works with Blinka a variation of https://github.com/adafruit/Adafruit_Blinka
"""

from xpander import Xpander
import time

# create an instance of the Xpander class as the PLC
PLC = Xpander()

# show an array of red leds in different intensities
buffer = [10] * 48
# white
PLC.RGBon(buffer)
time.sleep(1)
PLC.RGBoff()

# Set all LEDs to green
c = 1
for i in range(0, 48, 3):
    buffer[i] = c
    buffer[i + 1] = 0
    buffer[i + 2] = 0
    c += 1
PLC.RGBon(buffer)
time.sleep(1)
PLC.RGBoff()

# Set all LEDs to red
c = 0
for i in range(0, 48, 3):
    buffer[i] = 0
    buffer[i + 1] = c
    buffer[i + 2] = 0
    c += 1
PLC.RGBon(buffer)
time.sleep(1)
PLC.RGBoff()

# Set all LEDs to blue
c = 0
for i in range(0, 48, 3):
    buffer[i] = 0
    buffer[i + 1] = 0
    buffer[i + 2] = c
    c += 1
PLC.RGBon(buffer)
time.sleep(1)

# Set all LEDs to off
PLC.RGBoff()
