# PicoXpander test code
# Verifies operation of all onboard (GPIO) LED's

import digitalio
import board
import time

pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5,
        board.GP6, board.GP7, board.GP8, board.GP9, board.GP10,
        board.GP11, board.GP12, board.GP13, board.GP14, board.GP15,
        board.GP16, board.GP17, board.GP18, board.GP19, board.GP20,
        board.GP21, board.GP22, board.GP26, board.GP27, board.GP28]

# Configuration for each pin (All the same for now, but can be uniquely setup too)
configs = [
    {'pin': pins[x], 'direction': digitalio.Direction.OUTPUT, 'init_value': False}
    for x in range(len(pins))
]
gpio = []

for config in configs:
    print(config)
    pin = digitalio.DigitalInOut(config['pin'])
    pin.direction = config['direction']
    pin.value = config['init_value']
    gpio.append(pin)
    
while True:
    for x in range(len(gpio)):
        gpio[x].value = True
        if x > 0:
            gpio[x-1].value = False   
        time.sleep(0.1)
    
    gpio[len(gpio)-1].value = False

    for x in range(len(gpio)-2,0,-1):
        gpio[x].value = True
        gpio[x+1].value = False   
        time.sleep(0.1)
    
    gpio[1].value = False
