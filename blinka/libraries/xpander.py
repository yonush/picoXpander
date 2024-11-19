'''
    Pico I/O mapping as a Programmable Logic controller
    This file provides the digital input and output mapping 
    
    I/O mapping file as per the diagram Pico-OpenPLC-A4-Pinout.pdf
'''
import os
import sys
import time

# this environmental variable must be set, either in the code or from a terminal
#  otherwise the U2IF device will not be detected
try:
    if os.name == 'nt':
        os.environ["BLINKA_U2IF"] = "1"
        sys.path.insert(0, os.path.abspath('./lib'))
except:
    print("Using Circuitpython/Micropython")

#import adafruit_ssd1306
import analogio
import board
import busio
import digitalio
import pwmio
import sh1106


#uart = usb_cdc.console
#UART = usb_cdc.data
class Xpander:
    # ---- picoPLC addtional I/O MAPPING
    ONEWIRE = board.GP22
    IX0 = IX1 = IX2 = IX3 = IX4 = IX5 = IX6 = IX7 = digitalio.DigitalInOut
    QX0 = QX1 = QX2 = QX3 = QX4 = QX5 = QX6 = QX7 = digitalio.DigitalInOut

    GPIN = [IX0, IX1, IX2, IX3, IX4, IX5, IX6, IX7]
    GPOUT = [QX0, QX1, QX2, QX3, QX4, QX5, QX6, QX7]

    # onboard led used for runtime activity
    LED = board.LED
    
    # analogue outputs & PWM - defaults to 1KHz
    QW0 =  None
    QW1 = None
    PWM1 = AOUT1 = QW0 = None
    PWM2 = AOUT2 = QW1 = None

    # analogue inputs
    IW0 = ADC0 = None
    IW1 = ADC1 = None
    IW2 = ADC2 = None

    # I2C & UART
    SDA = board.SDA # data out
    SCL = board.SCL # data in    
    TX = board.TX
    RX = board.RX
    UART = None
    I2C = None
    OLED = None

    # SPI
    SPI_RX  = board.MISO
    SPI_CS  = board.CS0
    SPI_SCK = board.SCLK
    SPI_TX  = board.MOSI

    def __init__(self):
        self.LED = digitalio.DigitalInOut(board.LED)
        self.LED.direction = digitalio.Direction.OUTPUT
        self.QW0 =  pwmio.PWMOut(board.GP5, duty_cycle=2 ** 15, frequency=1000)
        self.QW1 = pwmio.PWMOut(board.GP4, duty_cycle=2 ** 15, frequency=1000)
        self.IW0 = self.ADC0 = analogio.AnalogIn(board.ADC0)
        self.IW1 = self.ADC1 = analogio.AnalogIn(board.ADC1)
        #self.IW2 = self.ADC2 = analogio.AnalogIn(board.ADC2)

        self.setI2C(self.SCL,self.SDA)
        self.setUART(self.TX,self.RX)
        self.setGPIO()
        self.setOLED(128,64)

    def setI2C(self,SCL,SDA):    
        # setup the I2C interface - default 400KHz
        try:
            self.I2C = busio.I2C(SCL, SDA, frequency=400_000)
            while not self.I2C.try_lock(): pass
            print("I2C addresses found:", [hex(device_address) for device_address in self.I2C.scan()])
            self.I2C.unlock()
        except:
            self.I2C = None
            print("No I2C device attached")
    
    def setUART(self,TX,RX):    
        try:
            self.UART = busio.UART(TX,RX, baudrate=115200, timeout=1)
        except:
            print("No UART capability found")
            self.UART = None   
    
    def setGPIO(self):    
        # ----- define the inputs and outputs
        ipins = [board.GP6,  board.GP7,  board.GP8,  board.GP9, 
                board.GP10, board.GP11, board.GP12, board.GP13]
            
        opins = [board.GP14, board.GP15, board.GP16, board.GP17, 
                board.GP18, board.GP19, board.GP20, board.GP21]
        
        for v in range(8):    
            # create output pins
            po = digitalio.DigitalInOut(opins[v])
            po.direction = digitalio.Direction.OUTPUT
            po.value = False
            self.GPOUT[v] = po

            # create input pins
            pi = digitalio.DigitalInOut(ipins[v])
            pi.direction = digitalio.Direction.INPUT
            pi.pull = digitalio.Pull.DOWN
            self.GPIN[v] = pi

    def setOLED(self,W,H):
        if not self.I2C: return
        if not self.OLED is None:
            del self.OLED
        try:
            self.OLED = sh1106.SH1106_I2C(W, H, self.I2C, addr=0x3c)    
        except:
            self.OLED = None    
            print("No OLED attached")

    def testOLED(self):
        if not self.I2C: 
            self.setOLED(128,64)
            #self.OLED = adafruit_ssd1306.SSD1306_I2C(128, 64, self.I2C) # 0.96" OLED
        if not self.OLED: return 

        self.OLED.fill(False)
        self.OLED.text("Hello world!", 0, 0, 1)
        self.OLED.text("picoXpander", 0, 10, 1)
        self.OLED.text("Version 1.0", 0, 20, 1)
        self.OLED.show()

def pollOut(PLC,delay):
    for i in range(8):        
        PLC.GPOUT[i].value = True
        time.sleep(delay)
        PLC.GPOUT[i].value = False

def pollIn(PLC,delay):
    toggle = False
    # scan through the inputs
    for i in range(8):                
        # if the input is high toggle the out twice
        if PLC.GPIN[i].value:
            PLC.GPOUT[i].value = True
            time.sleep(delay)
            PLC.GPOUT[i].value = False
            time.sleep(delay)
            PLC.GPOUT[i].value = True
            time.sleep(delay)
            PLC.GPOUT[i].value = False
            toggle = True
            time.sleep(delay)

    return toggle

if __name__ == "__main__":
    PLC = Xpander()
    PLC.testOLED()

    flag = True
    while True:

        # keep scanning whilst there is an input
        flag = pollIn(PLC,0.1)

        if not flag:
            # pollOut(0.2)
            pollOut(PLC,0.05)

    # these lines used to confirm code is running in the loop
        PLC.LED.value = not PLC.LED.value
        time.sleep(1.0)
