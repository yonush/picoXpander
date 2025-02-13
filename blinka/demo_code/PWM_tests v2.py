"""
    picoXpander PWM test using the ADC0
    Verifies operation of the analog out/PWM channels with the ADC
    LDR or potentiometer attached to ADC0 and servo attached to PWM0/AOUT0
    
    This code also works with Blinka a variation of https://github.com/adafruit/Adafruit_Blinka

    Version 0.0.2
"""

import time

from xpander import Xpander

PLC = Xpander()

if __name__ == "__main__":
    # sets freq for both AOUT0 & AOUT1
    PLC.setPWM(50)
    # AOUT0 & AOUT1 share the same PWM channel but the following line will return
    # the error "PWM different frequency on same slice." so use the above function instead
    # PLC.AOUT0.frequency = 50
    PLC.AOUT0.duty_cycle = 0
    PLC.AOUT1.duty_cycle = 0

    lower = 65535
    upper = 0
    while True:

        # read in the analog value from the potentiometer or LDR
        analog = PLC.ADC0.value
        lower = min(analog, lower)
        upper = max(analog, upper)
        print(f"min {lower} max{upper}")
        # range for the pot/ldr needs to be measured
        duty = PLC.map_range(analog, 19888, 65520, 0, 32767)

        PLC.AOUT0.duty_cycle = duty
        PLC.AOUT1.duty_cycle = duty

        # these lines used to confirm code is running in the loop
        PLC.LED.value = not PLC.LED.value
        time.sleep(0.05)
