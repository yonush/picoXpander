"""
    picoXpander driver board LED tester
    Verifies operation of all onboard (GPIO) LED's
    This demo code does not use the picoXpander library or Blinka
    
    version 0.0.2  
"""

import os
import sys

# this environmental variable must be set, either in the code or from a terminal
#  otherwise the U2IF device will not be detected
os.environ["BLINKA_U2IF"] = "1"
sys.path.insert(0, os.path.abspath("lib"))

import board
import digitalio

pins = [
    board.GP0,
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP21,
    board.GP22,
    board.GP26,
    board.GP27,
    board.GP28,
]

# Configuration for each pin (All the same for now, but can be uniquely setup too)
configs = [
    {"pin": pins[x], "direction": digitalio.Direction.OUTPUT, "init_value": False}
    for x in range(len(pins))
]
gpio = []

for config in configs:
    pin = digitalio.DigitalInOut(config["pin"])
    pin.direction = config["direction"]
    pin.value = config["init_value"]
    gpio.append(pin)

print("IO pins and other variables")
print(dir(board))

# start the LED test
for i in range(10):
    for x in range(len(gpio)):
        gpio[x].value = True
        if x > 0:
            gpio[x - 1].value = False
        # time.sleep(0.05)

    gpio[len(gpio) - 1].value = False

    for x in range(len(gpio) - 2, 0, -1):
        gpio[x].value = True
        gpio[x + 1].value = False
        # time.sleep(0.05)

    gpio[1].value = False

for x in range(len(gpio)):
    gpio[x].value = False
