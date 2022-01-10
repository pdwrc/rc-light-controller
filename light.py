try:
    from machine import Pin, PWM
except ModuleNotFoundError:
    from machine_mock import Pin, PWM

import time
import config

class LightState:
    OFF = 0
    LOW = 1
    HIGH = 2

class Animation:
    double_flash = ((0, 0), (100, 100), (0, 250), (100, 350), (0, 500), (0, 900))

    def multi_flash(n, start = 150, on = 150, off = 150):
        seq = [(0,0)]
        for i in range(n):
            seq.append((75, start + (on+off) * i))
            seq.append((0, start + (on+off) * i + on))
        seq.append((0,n * (on+off) + 100))
        print(seq)
        return seq

    simple_flash = ((100, 0), (0, 50))
    pulse = (
            (0, 0), (20, 50), (40, 100), (60, 150), (40, 200), (20, 250), (0, 300),
            (20, 350), (40, 400), (60, 450), (40, 500), (20, 550), (0, 600))

    def fade(from_level, to_level, speed = None):
        if speed is None:
            speed = config.config.fade_speed
        step = (to_level - from_level) / 5
        return list((int(from_level + step * x), x * speed) for x in range(5))

    def join(*args):
        t = 0
        animation = []
        for anim in args:
            for (val, tt) in anim:
                animation.append((val, tt + t))
            t += anim[-1][1]

        return animation


class Light:

    def __init__(self, config, no_pwm = False):
        self.pin = config.pin
        self.config = config
        if no_pwm:
            self.output = Pin(self.pin, Pin.OUT)
            self.pwm = None
        else:
            self.pwm = PWM(Pin(self.pin, Pin.OUT))
            self.pwm.freq(1000)
            self.pwm.duty_u16(0)
        self.level = 0
        self.animation = None
        self.cur_level = None


    def show_level(self, level):
        if self.cur_level is None or level != self.cur_level:
            #print("Showing %d on %d" % (level, self.pin))
            if self.pwm:
                self.pwm.duty_u16(int(0xFFFF * level / 100))
            else:
                self.output.value(1 if level > 50 else 0)
        self.cur_level = level

    def set_level(self, level):
        if self.animation is None:
            self.show_level(level)
        self.level = level

    def update(self, light_state, brake, flash):
        if self.animation is not None:
            self.tick()
        else:
            if self.config.brake > 0 and brake:
                new_level = self.config.brake
            elif self.config.flash > 0 and flash:
                new_level = self.config.flash
            elif light_state == LightState.HIGH:
                new_level = self.config.mode2
            elif light_state == LightState.LOW:
                new_level = self.config.mode1
            else:
                new_level = 0
            if new_level != self.level:
                self.animate(Animation.fade(self.level, new_level))
            self.set_level(new_level)

    def animate(self, animation, callback = None):
        self.animation_start = time.ticks_ms()
        self.animation = animation
        self.animation_callback = callback
        self.show_level(animation[0][0])

    def tick(self):
        if self.animation is not None:
            t = time.ticks_ms() - self.animation_start
            for i, (value, ta) in enumerate(self.animation):
                if t > ta and (i == len(self.animation) - 1 or t < self.animation[i+1][1]):
                    self.show_level(value)

                    if i == len(self.animation) - 1:
                        self.animation = None
                        if self.animation_callback is not None:
                            self.animation_callback(self)

        else:
            self.show_level(self.level)

