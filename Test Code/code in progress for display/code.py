# PicoXpander test code
# Verifies operation of all onboard (GPIO) LED's

import digitalio
import board
import time
import adafruit_ssd1306
import busio

# setup the I2C interface
i2c = busio.I2C(board.GP1, board.GP0, frequency=100_000)
while not i2c.try_lock(): pass
print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])
i2c.unlock()

# attach an oled = adafruit_ssd1306.SSD1306_I2C(128, Y, i2c, addr=0x3C)
# change the 32 to 64 for the larger oled
#YRES = 32 # smaller thin OLED display
YRES = 128 # larger square OLED display
oled = adafruit_ssd1306.SSD1306_I2C(128, YRES,i2c)
oled.fill(False)
oled.show()

pins = [ #board.GP0, board.GP1,
    board.GP2, board.GP3, board.GP4, board.GP5,
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
    #pin.pull = digitalio.Pull.DOWN # Use pull downs to ensure digital inputs are in a known state
    pin.value = config['init_value']
    gpio.append(pin)

def dispOLED():
    oled.fill(False) 
    txt = f"Loop Num: {loop_tally:.1f}" # Formatted string literal (Temperature)
    oled.text(txt, 0, 0, 1)
    txt = "Hello World" # Formatted string literal (Temperature)
    oled.text(txt, 0, 10, 1)
    txt = "PicoPLC testing..." # Formatted string literal (Temperature)
    oled.text(txt, 0, 20, 1)
    oled.show()

loop_tally = 0 # Track the number of times the LED's have been cycled through

while True:
    dispOLED()
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


