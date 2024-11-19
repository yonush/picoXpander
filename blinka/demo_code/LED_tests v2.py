import time
from xpander import Xpander
PLC = Xpander()

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