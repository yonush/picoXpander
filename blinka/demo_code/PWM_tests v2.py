"""
    picoXpander PWM test using the ADC0
    Verifies operation of the analog out/PWM channels with the ADC
    LDR or potentiometer attached to ADC0 and servo attached to PWM0/AOUT0
"""
import time

from xpander import Xpander

PLC = Xpander()

if __name__ == "__main__":
    PLC.setPWM(50)
    PLC.AOUT0.duty_cycle = 0
    PLC.AOUT1.duty_cycle = 0

    lower = 65535
    upper = 0
    while True:

        analog = PLC.ADC0.value
        lower = min(analog, lower)
        upper = max(analog,upper)
        print(f"min {lower} max{upper}")
        # range for the pot/ldr needs to be measured
        duty = PLC.map_range(analog,19888,65520,0,32767)   

        PLC.AOUT0.duty_cycle = duty
        PLC.AOUT1.duty_cycle = duty

    # these lines used to confirm code is running in the loop
        PLC.LED.value = not PLC.LED.value
        time.sleep(0.05)