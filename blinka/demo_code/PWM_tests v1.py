"""
    picoXpander PWM test
    Verifies operation of the two analog out/PWM channels
"""
import time

from xpander import Xpander

PLC = Xpander()


if __name__ == "__main__":
    # sets freq for both AOUT0 & AOUT1
    PLC.setPWM(200)
    # AOUT0 & AOUT1 share the same PWM channel but the following line will return
    # the error "PWM different frequency on same slice." so use the above function instead
    # PLC.AOUT0.frequency = 100 
    PLC.AOUT0.duty_cycle = 0
    PLC.AOUT1.duty_cycle = 0
    
    duty = 0
    SERVO_MAX = 50
    while True:

        # cap the upper end of the servo range
        if duty > SERVO_MAX:
           duty = 0
        
        # map duty cycle 0-100% to Pico 0-65535}
        duti = PLC.map_range_zero(duty,100,65535)   
        PLC.AOUT0.duty_cycle = duti
        PLC.AOUT1.duty_cycle = duti
        duty += 1

    # these lines used to confirm code is running in the loop
        PLC.LED.value = not PLC.LED.value
        time.sleep(0.05)