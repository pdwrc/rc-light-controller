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

    def multi_flash(n, start = 150, on = 150, off = 150, invert = False):
        seq = [(0,0)]
        a = 75 if not invert else 0
        b = 0 if not invert else 75
        for i in range(n):
            seq.append((a, start + (on+off) * i))
            seq.append((b, start + (on+off) * i + on))
        seq.append((b,n * (on+off) + off))
        return seq

    simple_flash = ((100, 0), (0, 50), (0, 100))
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
        if type(config.pin) in (list, tuple):
            self.pins = config.pin
        else:
            self.pins = [config.pin]

        self.config = config
        if no_pwm:
            self.outputs = list(Pin(pin, Pin.OUT) for pin in self.pins)
            self.pwms = None
        else:
            self.pwms = list(PWM(Pin(pin, Pin.OUT)) for pin in self.pins)
            for pwm in self.pwms:
                pwm.freq(1000)
                pwm.duty_u16(0)
        self.level = 0
        self.animation = None
        self.cur_level = None


    def menu_scale(self, level, menu):
        if menu:
            return int(level * self.config.menu/100)
        return level

    def show_level(self, level):
        if self.cur_level is None or level != self.cur_level:
            if self.pwms:
                for pwm in self.pwms:
                    pwm.duty_u16(int(0xFFFF * level / 100))
            else:
                for output in self.outputs:
                    output.value(1 if level > 50 else 0)
        self.cur_level = level

    def set_level(self, level, menu = False):
        level = self.menu_scale(level, menu)
        if self.animation is None:
            self.show_level(level)
        self.level = level

    def update(self, now, light_state, brake, flash):
        if self.animation is not None:
            self.tick(now)
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

    def animate(self, animation, callback = None, loop = False, now = None, menu = False):
        if animation is not None:
            self.menu_animation = menu
            self.animation_start = now if now is not None else time.ticks_ms()
            self.animation = animation
            self.animation_loop = loop
            self.animation_callback = callback
            self.show_level(self.menu_scale(animation[0][0], menu))
        else:
            self.animation = None
            self.show_level(self.level)

    def tick(self, now = None):
        if now is None:
            now = time.ticks_ms()
        if self.animation is not None:
            t = now - self.animation_start
            for i, (value, ta) in enumerate(self.animation):
                if t > ta and (i == len(self.animation) - 1 or t < self.animation[i+1][1]):
                    self.show_level(self.menu_scale(value, self.menu_animation))

                    if i == len(self.animation) - 1:
                        if self.animation_loop:
                            self.animate(self.animation, loop = True) #, now = 2 * now - self.animation_start - self.animation[-1][1] , loop = True)
                        else:
                            self.animation = None
                            if self.animation_callback is not None:
                                self.animation_callback(self, now)

        else:
            self.show_level(self.level)

