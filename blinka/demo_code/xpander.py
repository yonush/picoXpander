'''
    Pico I/O mapping as a Programmable Logic controller
    This file provides the digital input and output mapping to be used with 
    the picoXpander and picoPLC
    
    I/O mapping file as per the diagram Pico-OpenPLC-A4-Pinout.pdf
    version 0.0.5
'''

import os
import sys
import time

# this environmental variable must be set, either in the code or from a terminal
#  otherwise the U2IF device will not be detected for blinka
try:
    # This only works under blinka, ignore otherwise 
    if (not "uname" in dir(os)) and os.name == 'nt':
        import platform

        isEmbedded = False
        os.environ["BLINKA_U2IF"] = "1"
        sys.path.insert(0, os.path.abspath('./lib'))
        print(f"Using Python {platform.python_version()} on {platform.system()}")
except:
    isEmbedded = True
    print("Using Circuitpython/Micropython")

# Make sure a pico is attached before tryning to use the library
try: 
    import analogio
    import board
    import busio
    import digitalio
    import neopixel_write
    import pwmio

    # check setOLED() for the contextual loading of the imports
    #import sh1106  # works for the ssd1306 driver chips with 64 height too
    #import adafruit_ssd1306
except:
    print("ERR: No Raspberry Pico with U2IF firmware attached")
    exit()

#uart = usb_cdc.console
#UART = usb_cdc.data
class Xpander:
    # ---- picoPLC addtional I/O MAPPING
    # one wire support for Dallas devices, DHT, etc. 
    ONEWIRE = board.GP22

    # group the inputs and outputs into lists for easy access
    GPIN:list = [digitalio.DigitalInOut] * 8
    GPOUT:list = [digitalio.DigitalInOut] * 8

    # I2C,SPI & UART
    # - I2C
    SDA = board.SDA # data out
    SCL = board.SCL # data in    

    # - SPI
    SPI_RX  = board.MISO
    SPI_CS  = board.CS0
    SPI_SCK = board.SCLK
    SPI_TX  = board.MOSI

    # - UART
    # support is still under development for the Blinka
    TX = board.TX 
    RX = board.RX
    
    # OLED settings
    OLEDw = 128  # assumed and not used
    OLEDh = 64
    OLEDlines = 6 # lines of text on the OLED
    OLEDdata = [""] * OLEDlines

    def __init__(self):
        self.LED:digitalio.DigitalInOut = digitalio.DigitalInOut(board.LED)
        self.LED.direction = digitalio.Direction.OUTPUT
        self.IW0 = self.ADC0 = analogio.AnalogIn(board.ADC0)
        self.IW1 =  self.ADC1 = analogio.AnalogIn(board.ADC1)     
        self.AOUT0 = self.PWM0 = self.QW0 = None
        self.AOUT1 = self.PWM1 = self.QW1 = None   
        if isEmbedded:            
            # has issues under Blinka
            self.IW2 =  self.ADC2 = analogio.AnalogIn(board.ADC2)

        # assume no peripherals are set or attached
        self.UART = self.I2C = self.OLED = self.SPI = None        
        self.setGPIO()

    def init_all(self):
        """ Initialiase the peripheral interfaces together

            I2C, SPI, UART, OLED
        """

        self.setI2C()
        self.setSPI()
        self.setUART() # default 115200 baud
        self.setPWM() # default to 1KHz
        self.setOLED() # default height 64 pixels

    def setPWM(self,freq=1000):
        """ Initialise the PWM frequency and IO pins\n
            Both channels are set at the same time as they share the same PWM slice.

        Args:
            freq (int): set the PWM frequency 10 (10HZ) - 1_000_000 (1MHz)
        """
        try:
            freq = int(freq)
        except:
            return
                    
        if freq < 10 or freq > 1_000_000: return
        if not self.QW0 is None:
            self.QW0.deinit()
        if not self.QW1 is None:
            self.QW1.deinit()

        print(f"Initialising PWM to {freq}Hz on GP{board.AOUT0.id} & GP{board.AOUT1.id}")    
        try:
            self.QW0 = pwmio.PWMOut(board.AOUT0, duty_cycle=0, frequency=freq, variable_frequency=True)
            self.QW1 = pwmio.PWMOut(board.AOUT1, duty_cycle=0, frequency=freq, variable_frequency=True)
        except:
            print(f"Error setting the PWM to {freq}Hz on GP{board.AOUT0.id} & GP{board.AOUT1.id}")
            self.AOUT0 = self.PWM0 = self.QW0 = None
            self.AOUT1 = self.PWM1 = self.QW1 = None
            return
        self.AOUT0 = self.PWM0 = self.QW0
        self.AOUT1 = self.PWM1 = self.QW1

    def setSPI(self):
        """ Initialiase the SPI on GP2,GP3,GP4,GP5
        """
        print(f"Initialising SPI to GP{board.SCLK.id}, GP{board.MISO.id} & GP{board.MOSI.id}")            
        self.SPI_CS = digitalio.DigitalInOut(self.SPI_CS)
        try:
            self.SPI = busio.SPI(self.SPI_SCK, MOSI=self.SPI_TX, MISO=self.SPI_RX)
        except:
            print("No SPI devices found")
            self.SPI = None   

    def setI2C(self):    
        """ Initialise the I2C on GP0,GP1 @ 400KHz
        """
        print(f"Initialising the I2C on GP{board.SCL.id},GP{board.SDA.id} @ 400KHz")
        try:
            self.I2C = busio.I2C(self.SCL, self.SDA, frequency=400_000)
            poll = 0
            while not self.I2C.try_lock() and poll < 10: poll += 1
            print("I2C addresses found:", [hex(device_address) for device_address in self.I2C.scan()])   
            self.I2C.unlock()

        except:
            self.I2C = None
            print("No I2C device attached")
    
    def setUART(self,baud=115200):    
        """ Initialiase the UART on GP4,GP5 @ 115200 baud
            default to 8N1 and no flow control

        Args:
            baud (int): UART baud rate 75 to 128000
        """
        print(f"Initialising UART to {baud} baud on GP{board.TX.id} & GP{board.RX.id}") 
        if not isinstance(baud,int): return
        # range based off windows COM settings          
        if not baud in (75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 7200,
                         9600, 14400, 19200, 38400, 57600, 115200,128000):
            return
        try:
            self.UART = busio.UART(self.TX,self.RX, baudrate=115200, timeout=1)
        except:
            print("No UART capability found")
            self.UART = None   
            
    def setGPIO(self):    
        """ Initialiase the I/O on GP6-GP13 for input and GP14-GP21 for output\n
            IX0-IX7 for inputs\n            
            QX0-QX7 for outputs
        """

        # ----- define the inputs and outputs
        ipins = [board.GP6,  board.GP7,  board.GP8,  board.GP9, 
                board.GP10, board.GP11, board.GP12, board.GP13]
            
        opins = [board.GP14, board.GP15, board.GP16, board.GP17, 
                board.GP18, board.GP19, board.GP20, board.GP21]
        
        print(f"Initialising the GPIO on GP6-GP13 for input and GP14-GP21 for output")
        for v in range(8):    
            # create output pins
            self.GPOUT[v] = digitalio.DigitalInOut(opins[v])
            self.GPOUT[v].direction = digitalio.Direction.OUTPUT
            self.GPOUT[v].value = False
            self.QX0:digitalio.DigitalInOut = self.GPOUT[0]
            self.QX1:digitalio.DigitalInOut = self.GPOUT[1]
            self.QX2:digitalio.DigitalInOut = self.GPOUT[2]
            self.QX3:digitalio.DigitalInOut = self.GPOUT[3]
            self.QX4:digitalio.DigitalInOut = self.GPOUT[4]
            self.QX5:digitalio.DigitalInOut = self.GPOUT[5]
            self.QX6:digitalio.DigitalInOut = self.GPOUT[6]
            self.QX7:digitalio.DigitalInOut = self.GPOUT[7]
           
            # create input pins
            self.GPIN[v] = digitalio.DigitalInOut(ipins[v])
            self.GPIN[v].direction = digitalio.Direction.INPUT
            self.GPIN[v].pull = digitalio.Pull.DOWN
            self.IX0:digitalio.DigitalInOut = self.GPIN[0]
            self.IX1:digitalio.DigitalInOut = self.GPIN[1]
            self.IX2:digitalio.DigitalInOut = self.GPIN[2]
            self.IX3:digitalio.DigitalInOut = self.GPIN[3]
            self.IX4:digitalio.DigitalInOut = self.GPIN[4]
            self.IX5:digitalio.DigitalInOut = self.GPIN[5]
            self.IX6:digitalio.DigitalInOut = self.GPIN[6]
            self.IX7:digitalio.DigitalInOut = self.GPIN[7]
        

    def setOLED(self,is32:bool = False):
        """ Initialiase the OLED on the I2C
            SH1106 OLED with 128x64 resolution. 
            Supports the 0.96", 1.54" or 2.42" OLED with pixel heigh 64\n            
            0.91" with pixel height 32 uses the adafruit_SSD1306 driver.
        Args:
            is32 (bool): True for 32 pixel heigh. default False
        """
        if not self.I2C: return
        if not self.OLED is None:
            del self.OLED
        print(f"Initialising the 128x{32 if is32 else 64} OLED on I2C0")                     
        
        # only import the relevant OLED driver based on the OLED pixel height
        try:
            if is32:
                import adafruit_ssd1306
                self.OLED = adafruit_ssd1306.SSD1306_I2C(128, 32, self.I2C, addr=0x3c)    
            else: 
                import sh1106
                self.OLED = sh1106.SH1106_I2C(128, 64, self.I2C, addr=0x3c)    
        except:
            self.OLED = None    
            print("No OLED attached")

    # display 1 or more lines of text from a list onto the OLED
    def display(self,strs:list):
        """Send 1-6 strings to the OLED display assuming the 128x64 device

        Args:
            strs (list): List of 1-6 strings
        """
        
        if not self.OLED: return 
        if not isinstance(strs,list): return        
        if len(strs) > self.OLEDlines:
            strs = strs[:self.OLEDlines]
        self.OLED.fill(False)
        for k,v in enumerate(strs):
            try:
                # save updated line
                if isinstance(v,str) and len(v) > 0:
                    self.OLEDdata[k] = v
                self.OLED.text(self.OLEDdata[k],0,k * 10,1)
            except: 
                return
        self.OLED.show()        


    def testOLED(self):
        """ Print a test message on the OLED
        """
        if not self.I2C: 
            self.setOLED()            
        if not self.OLED: return 

        self.OLED.fill(False)
        self.OLED.text("Hello world!", 0, 0, 1)
        self.OLED.text("picoXpander", 0, 10, 1)
        self.OLED.text("Version 1.0", 0, 20, 1)
        self.OLED.show()


    def RGBon(self,buffer):
        """ Turn on an array of WS2812b/Neopixels
            Up to 16 GRB leds supported. 
            Board driver can support up to 1000
        
        Args:
            buffer (list): 16 x 3 GRB byte values
        """

        # 16 x 3 GRB 
        if not isinstance(buffer,list): return
        # clip the buffer
        if len(buffer) > 48: 
            buffer = buffer[:48]
        # clip large values to 1byte
        for i in range(len(buffer)):
            if isinstance(buffer[i],int):
                buffer[i] = buffer[i] & 0xFF
            else:
                buffer[i] = 0                

        neopixel_write.neopixel_write(self.ONEWIRE,buffer)

    def RGBoff(self):
        """ Turn off the WS281b leds - up to 16 of them
        
        Args:
            None
        Return:
            None    
        """

        buffer = [0] * 48
        neopixel_write.neopixel_write(self.ONEWIRE,buffer)

    def map_range(self,value:int, in_min:int, in_max:int, out_min:int, out_max:int)->int:
        """ Map a value from one range to another

        Args:
            value (int): value to map
            in_min (int): low end of from range
            in_max (int): upper end of from range
            out_min (int): low end of to range
            out_max (int): upper end of to range

        Returns:
            int: mapped integer
        """

        if not isinstance(value,int): return
        if not(isinstance(in_min,int) and isinstance(in_max,int)): return        
        if not(isinstance(out_min,int) and isinstance(out_max,int)): return
        return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def map_range_zero(self,value:int, in_max:int, out_max:int)->int:
        """ Map a value from one range to another assuming the ranges start at 0

        Args:
            value (int): value to map
            in_max (int): upper end of from range
            out_max (int): upper end of to range

        Returns:
            int: mapped integer
        """

        if not(isinstance(value,int) and isinstance(in_max,int) and isinstance(out_max,int)): return
        return value * out_max // in_max

# diagnostics test code
if __name__ == "__main__":
    def pollOut(PLC:Xpander,delay:float):
        """ Test the Outputs 
        """    
        for i in range(8):        
            PLC.GPOUT[i].value = True
            time.sleep(delay)
            PLC.GPOUT[i].value = False

    def pollIn(PLC:Xpander,delay:float):
        """ Test the inputs
        """    

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

    PLC = Xpander()
    PLC.init_all()
    # if the 0.96", 1.54" or 2.42" OLED is used then the height is default 64
    #PLC.setOLED(H=32)
    PLC.testOLED()
    time.sleep(1)
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
