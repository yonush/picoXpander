# Using Blinka with the picoXpander

The Blinka code and firmware lets you use microcontrollers to provide the external IO for a computer. Python code is written on the computer and IO instructions are sent to the device over USB. This will work with the picoXpander using a customised version of the Raspberry Pico firmware and a modded version of the Adafruit Blinka Python libraries.

## TODO
- Redraw the pinout image for picoXpander layout
- Fix UART - convert from hid to hidapi package
- Update documentation
- Write code for traffic light board
- Write up on changes to the various packages

## Programming languages & environment

The following programming languages are supported with the picoXpander kit.

- MicroPython (confirmed working)
- CircuitPython (incl. Blinka with custom U2IF code,c onfirmed working)
- Go with TinyGo (to be tested)
- Arduino C/C++ (confirmed working)
- OpenPLC with the IEC61131 PLC languages (confirmed working)
- Scratch with the Scratch 3 OneGPIO Extensions (to be tested)

Basically any language that can work on the Raspberry Pico is suitable for this kit.

## Resources

**Blinka resources**
- [Adafruit Blinka](https://github.com/adafruit/Adafruit_Blinka)
- [Adafruit Python PlatformDetect](https://github.com/adafruit/Adafruit_Python_PlatformDetect)
- [CircuitPython firmware](https://circuitpython.org/downloads)
- [CircuitPython Libraries](https://circuitpython.org/libraries)
- [mpy cross](https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/)

**U2IF support**
- [U2IF](https://github.com/execuc/u2if)
- [Adafruit U2IF](https://github.com/adafruit/u2if)

**Simulator & tutorials**
- [Wokwi](https://wokwi.com/)
- [CircuitPython Libraries on any Computer with Raspberry Pi Pico](https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico?view=all)
- [CircuitPython Libraries on MicroPython using the Raspberry Pi Pico](https://learn.adafruit.com/circuitpython-libraries-on-micropython-using-the-raspberry-pi-pico)
-[CoderDojo Twin Cities Micropython](https://www.coderdojotc.org/micropython/)

## I/O mapping for Blinka and OpenPLC with the picoXpander

- GP0,GP1 - I2C0
- GP2, GP3, GP4, GP5 - SPI0
- GP4,GP5 - UART1 (still under development)
- GP2,GP3 - PWM/Analog out as %QW0,%QW1 in OpenPLC 
- GP22 - 1-wire (DHT, Dallas, WS2812b, etc)
- GP26,GP27, GP28 ADC as %IW0-%IW2 in OpenPLC
- GP6-GP13 - Inputs as %IX0.0-%IX0.7 in OpenPLC
- GP14-GP21 - Outputs as %IX0.7-%IX0.0 in OpenPLC

GP2-4 can be used with SPI but not at the same time with the I2C and UART
GP4,5 can be used for the UART to connect two boards in a "network"
GP2,3,4,5,22,26,27,28 can be remapped for some boards and the breakout board

## Demos

Refer to the demos below on how to use the Xpander boards 
- xpander.py - the main library 
- blinka_test.py - check if the blinka setup is working
- ball.py - bounce a ball on the OLED
- LED_tests v1.py - scroll through the board LEDS
- LED_tests v2.py - test the 8bitio board (leds & buttons)
- rgb_pixels.py - test the ws2812b/neopixel interface
- MAX7219.py - test the SPI using the MAX7219 LED matrix
- gui.py - using guizero to show gui interaction with the kit
- PWM_tests v1.py - test the PWM channels (assuming a servo or led is attached)
- PWM_tests v2.py - drive a PWM pin from an analog input (assuming a servo and LDR are attached)
- usb_check.py - short USB check for the custom U2IF firmware

## Pico preparation for Python and U2IF

The Pico and the computer needs to be prepared before the Blinka can work

### Step 1 - install Python packages onto the computer**
We can assume Python has already been installed and a suitable Editor is ready

Do not install the *hid* package only the *hidapi*

    pip install hidapi
    pip install pyserial
    pip install Adafruit-PlatformDetect

**Modified adafruit-blinka module**
Normally the following would be installed but we are using a custom version to support the picoXpander boards.

    pip install adafruit_blinka

The *Adafruit_Blinka_picoXpander* has been modified to support the functionality and pin layout for the Pico to be used with the picoXpander driver board. Use the following version of the module 

    pip install adafruit_blinka_picoXpander.zip

**Changes made to adafruit-blinka module**

- src\busio.py (add suport for UART - wip)
- src\adafruit_blinka\board\pico_u2if.py (updated pin map)
- src\adafruit_blinka\microcontroller\rp2040_u2if\rp2040_u2if (line 404 should be gpio.id)
- src\adafruit_blinka\microcontroller\rp2040_u2if\i2c.py (updated pin map for I2C - channel 0 GPOP0 & GPIO1)
- src\adafruit_blinka\microcontroller\rp2040_u2if\spi.py (updated pin map for SPI)
- src\adafruit_blinka\microcontroller\rp2040_u2if\uart.py (copied from rp2040 - wip)


**BLINKA_U2IF environment variable**
Under Windows an environment variable must be set otherwise you will get unsupported device errors.
Using the old console or PowerShell

    setx BLINKA_U2IF 1

You can add the following code to the top of your program

    import os
    os.environ["BLINKA_U2IF"] = "1"

### Step 2 - Prepare the Pico

The pico requires a custom firmware that configures the I/O and waits for commands from the computer. The commands are sent over USB.
Use the firmware in this folder [picoXpander U2IF FW](firmware/) to prepare the pico. They have been compiled to support the Pico, Pico W, Pico 2, Pico 2 W and mapped for the picoXpander interfaces. This is a modified version of the **adafruit_u2if** to support the alternate pin layout used by the picoXpander.

### Step 3 - Testing the setup

Assuming the installation and configuration went well, the next step is to make sure Python code on the computer can communicate and control the picoXpander. Load up the following file into your editor (E.g Thonny or VScode) then run the code. It should give you some diagnostics information then proceed to blink two LEDs on the picoXpander driver board

[Blinka test](blinka_test.py)

The following code can be used to test all of the IO leds on the picoXpander driver board.

[LED test](LED_tests.py)


## [optional] Using Blinka using CircuitPython instead of using U2IF firmware 

This should work for the Raspberry Pico W and Raspberry Pico 2 that do not have a U2IF firmware.

*Note the UART code is still under development*

- Install the relevant CircuitPython firmware from the *firmware* folder
- Navigate to the modules folder 
    - upload the *adafruit_platformdetect* folder to the /lib on the Pico. 
    - navigate *Adafruit_Blinka\src\adafruit_blinka\microcontroller*
    - delete everything except generic_agnostic_board, generic_micropython, rp2040 and rp2040_u2if
    - upload the entire contents of the *src* folder to the Pico /lib folder
- Navigate to the *Libraries* folder
    - only copy selected libraries to the Pico /lib folder