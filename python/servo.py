try:
    from machine import Pin, PWM
except ImportError:
    from machine_mock import Pin, PWM

class Servo:

    def __init__(self, pin, channel):
        self.channel = channel
        self.cur_level = None
        self.pwm = PWM(Pin(pin, Pin.OUT))
        self.follows_light = 0
        self.pwm.freq(50)
        self.set_level(0)

    def set_level(self, level):
        if self.cur_level != level:
            duty = 0xFFFF - ((1500 + 5 * level) * 0xFFFF // 20000)
            self.pwm.duty_u16(duty)
            self.cur_level = level

    
