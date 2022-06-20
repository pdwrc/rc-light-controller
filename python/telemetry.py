from animation import SimpleAnimation
from button import ButtonEvent
import time

class Telemetry:

    def __init__(self, vehicle):
        self.vehicle = vehicle


    def click(self, event, count = None):
        if event == ButtonEvent.SHORT_CLICK:
            for l in self.vehicle.lights:
                l.set_level(0)
                l.animate(None)
            if self.position >= 3:
                return False
            self.position += 1
            if self.position == 1:
                print("Low voltage")
                if self.vehicle.voltage is not None and self.vehicle.cells is not None:
                    self.do_number_animation(self.vehicle.low_voltage//self.vehicle.cells)
            elif self.position == 2:
                print("Temperature")
                if self.vehicle.esc_temperature is not None:
                    self.do_number_animation(self.vehicle.esc_temperature)
            elif self.position == 3:
                print("EXT Temperature")
                if self.vehicle.ext_temperature is not None:
                    print(self.vehicle.ext_temperature)
                    self.do_number_animation(self.vehicle.ext_temperature, callback = self.done)
        return True

    def done(self, animation, now):
        self.vehicle.in_telemetry = False

    def number_animation(self, voltage):
        values = list((voltage // div) % 10 for div in (100, 10 ,1))
        a = []
        non_zero = False
        for v in values:
            a.append(SimpleAnimation(((0,750),)))
            if v > 0:
                non_zero = True
                a.append(SimpleAnimation.multi_flash(v, on = 250, off = 250))
            elif non_zero:
                a.append(SimpleAnimation.multi_flash(1, on = 750, off = 250))

        a.append(SimpleAnimation(((0,750),)))
        return SimpleAnimation.join(*a)

    def do_number_animation(self, value, callback = None):
        anim = self.number_animation(value)
        now = time.ticks_ms()
        for i, l in enumerate(self.vehicle.lights + [self.vehicle.status_led]):
            l.animate(anim, now = now, callback = callback if i == 0 else None)

    def start(self):
        for l in self.vehicle.lights:
            l.set_level(0)
        self.position = 0
        if self.vehicle.voltage is not None and self.vehicle.cells is not None:
            self.do_number_animation(self.vehicle.voltage//self.vehicle.cells)

