try:
    from machine import Pin, PWM
except ModuleNotFoundError:
    from machine_mock import Pin, PWM

import time
import vehicle

class Animation:
    double_flash = ((0, 0), (100, 100), (0, 250), (100, 350), (0, 500), (0, 900))

    def multi_flash(n):
        start = 150
        on = 150
        off = 100
        seq = [(0,0)]
        for i in range(n):
            seq.append((100, start + (on+off) * i))
            seq.append((0, start + (on+off) * i + on))
        seq.append((0,n * (on+off) + 100))
        print(seq)
        return seq


class Light:

    def __init__(self, pin, off = 0, on = 90, brake = None, flash = None):
        self.pin = pin
        self.pwm = PWM(Pin(pin, Pin.OUT))
        self.pwm.freq(1000)
        self.pwm.duty_u16(0)
        self.level = 0
        self.off_level = off
        self.on_level = on
        self.brake_level = brake
        self.flash_level = flash
        self.animation = None
        self.cur_level = None

    def as_dict(self):
        return {
            "pin": self.pin,
            "off": self.off_level,
            "on": self.on_level,
            "flash": self.flash_level,
            "brake": self.brake_level
        }

    def show_level(self, level):
        if self.cur_level is None or level != self.cur_level:
            print("Showing %d on %d" % (level, self.pin))
            self.pwm.duty_u16(int(0xFFFF * level / 100))
        self.cur_level = level

    def set_level(self, level):
        if self.animation is None:
            self.show_level(level)
        self.level = level

    def update(self, light_state, brake, flash):
        if self.animation is not None:
            self.tick()
        else:
            if self.brake_level is not None and brake:
                new_level = self.brake_level
            elif self.flash_level is not None and flash:
                new_level = self.flash_level
            elif light_state == vehicle.LightState.HIGH:
                new_level = self.on_level
            elif light_state == vehicle.LightState.LOW:
                new_level = self.off_level
            else:
                new_level = 0
            self.set_level(new_level)

    def animate(self, animation):
        self.animation_start = time.ticks_ms()
        self.animation = animation
        self.show_level(animation[0][0])

    def tick(self):
        if self.animation is not None:
            t = time.ticks_ms() - self.animation_start
            for i, (value, ta) in enumerate(self.animation):
                if t > ta and (i == len(self.animation) - 1 or t < self.animation[i+1][1]):
                    self.show_level(value)

                    if i == len(self.animation) - 1:
                        self.animation = None

        else:
            self.show_level(self.level)

