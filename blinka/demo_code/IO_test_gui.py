"""
     Simple GUI example using the basic guizero Python package
     https://lawsie.github.io/guizero/

    This code also works with Blinka a variation of https://github.com/adafruit/Adafruit_Blinka

    Version 0.0.2
"""
import threading
import time

import guizero as gz
import xpander as IO

io = IO.Xpander()
io.init_all()
app = gz.App(layout="grid")

"""
  We need an event that can read data from the Pico on the picoXpander board.
  For this we setup a thread that polls the Pico at regular intervals
"""
isRunning = False # is the thread polling the Pico?
thread = None # thread to poll the Pico

# setup a thread to handle the button inputs from the IO board
class update_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        Polling()

# the function to run for the thread
def Polling():
    global isRunning,io
    # catchall exception
    try:
        if isRunning:
            buttons = ""
            for i in range(8):
                if io.GPIN[i].value:
                    waffle[i,0].color = "green"
                    LEDS[i].bg = "green"
                    buttons += f"{i} "
                else:
                    waffle[i,0].color = "red"
                    LEDS[i].bg = "red"   
            io.display(["",str(f"Buttons {buttons}"),"","","","",""])                    
        # set up an timed event
        app.after(100, Polling)                     
    except:
        isRunning = False        

# start/stop the polling the IO buttons
def evtStart():
    global isRunning,thread
    try:
        if isRunning:
            btnStart.text = "Start"                                
            isRunning = False
        else:
            btnStart.text = "Stop"                                
            isRunning = True
            # only initiate the thread once, but use a flag to control it
            if thread is None:  
                thread = update_thread()
                thread.daemon = True
                thread.start()            
    except Exception as e:
        print("unable to start update_thread, " + str(e))


# event to handle the GUI button presses
def evtButton(event_data):
    # get the button that was pressed
    b:gz.PushButton = event_data.widget
    # check which leds are lit and add to the list
    guib = ""
    for i in range(8):
        if io.GPOUT[i].value:
            guib += f"{i} "
    io.display([str(f"GUI {guib}"),"","","","",""])

    #  convert the button number into the IO address
    #led = eval(f"io.QX{b.text}")
    led = io.GPOUT[int(b.text)]
    # toggle the led on the board
    led.value = not led.value
    # change the button background based on led state
    if led.value:
        b.bg = "Green"
    else:
        b.bg = "Red"

def evtQuit():
    global isRunning
    #import usb_hid as dev
    #dev.disable()
    isRunning = False
    time.sleep(0.5) # let the thread stop
    exit()

if __name__ == "__main__":
    # buttons on IO board
    BUTTONS:list = []
    # leds on the IO board
    LEDS:list = []
    
    # use a waffle widget to represent a row of LEDS
    waffle = gz.Waffle(app,1,8,40,dotty=True,grid=[0,3])

    # create the variabous buttons for the leds and buttons
    led_box = gz.Box(app, height="fill", align="left", border=False, grid=[0,2,3,1],layout="grid")
    for i in range(8):
        b = gz.PushButton(led_box, text=str(i), align="left",grid=[i,0])
        b.bg = "Red"
        b.when_clicked = evtButton
        BUTTONS.append(b)

        l = gz.PushButton(led_box,text="      ", align="left", grid=[i,1])
        l.bg = "Red"
        LEDS.append(l)
        
        #waffle[i % 4, 0 if i < 4 else 1 ].color = "red"
        waffle[i,0].color = "red"

    gz.Text(app, text="Toggle Leds on the IO board using the numbered buttons",bg="yellow", grid=[0,4,3,1])
    gz.Text(app, text="Press Start/Stop to control the polling of the Pico",bg="yellow", grid=[0,5,3,1])

    btnStart = gz.PushButton(app, text="Start", grid=[0,6], command=evtStart)
    gz.PushButton(app, text="Quit", grid=[1,6], command=evtQuit)
    # span multiple columns/rows with [x,y,xspan,yspan]
    

    app.display()