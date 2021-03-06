try:
    from machine import Pin, PWM
except ImportError:
    from machine_mock import Pin, PWM

import time
import config
from animation import Fade

class LightState:
    OFF = 0
    LOW = 1
    HIGH = 2

class Light:

    def __init__(self, config, no_pwm = False, channel = None):
        if type(config.pin) in (list, tuple):
            self.pins = config.pin
        else:
            self.pins = [config.pin]

        self.config = config
        self.channel = channel
        if no_pwm:
            self.outputs = list(Pin(pin, Pin.OUT) for pin in self.pins)
            self.pwms = None
        else:
            self.pwms = list(PWM(Pin(pin, Pin.OUT)) for pin in self.pins)
            for pwm in self.pwms:
                pwm.duty_u16(0)
                pwm.freq(1000)
        self.level = 0
        self.animations = dict()
        self.cur_level = None
        self.min_animation_priority = None


    def menu_scale(self, level, menu):
        if menu:
            return level * self.config.menu/100
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

    def update(self, now, light_state, brake, flash, emergency):
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
                self.animate(Fade(self.level, new_level))
            self.set_level(new_level)

    def animate(self, animation, callback = None, loop = False, now = None, menu = False, priority = 0):
        if animation is not None:

            start = now if now is not None else time.ticks_ms()
            self.animations[priority] = animation
            animation.start(start, loop, callback)

            self.menu_animation = menu
            v = animation.value(start)
            if v is not None:
                scaled = self.menu_scale(v, menu)
                self.show_level(scaled)
        else:
            self.animations.pop(priority, None)
            if self.animation is None:
                self.show_level(self.level)
            else:
                self.tick(now)

    @property
    def animation(self):
        if len(self.animations) == 0:
            return None
        p = max(self.animations.keys())
        if self.min_animation_priority is None or p >= self.min_animation_priority:
            return self.animations[p]
        return None


    def tick(self, now = None):
        if now is None:
            now = time.ticks_ms()
        animation = self.animation
        if animation is not None:
            value = self.animation.value(now)
            if value is None:
                # Animation is complete
                self.animations.pop(max(self.animations.keys()))
                animation.done(self, now)
            else:
                self.show_level(self.menu_scale(value, self.menu_animation))
        else:
            self.show_level(self.level)

