from animation import SimpleAnimation
from button import ButtonEvent
import time

class Telemetry:

    def __init__(self, vehicle):
        self.vehicle = vehicle


    def click(self, event, count = None):
        if self.vehicle.voltage is None or self.vehicle.cells is None:
            return False
        if event == ButtonEvent.SHORT_CLICK:
            for l in self.vehicle.lights:
                l.set_level(0)
                l.animate(None)
            if self.position >= 1:
                return False
            self.position += 1
            self.do_voltage_animation(self.vehicle.low_voltage//self.vehicle.cells, callback = self.done)
        return True

    def done(self, animation, now):
        self.vehicle.in_telemetry = False

    def voltage_animation(self, voltage):
        values = list((voltage // div) % 10 for div in (100, 10 ,1))
        a = []
        for v in values:
            a.append(SimpleAnimation(((0,750),)))
            a.append(SimpleAnimation.multi_flash(v, on = 250, off = 250))
        a.append(SimpleAnimation(((0,750),)))
        return SimpleAnimation.join(*a)

    def do_voltage_animation(self, voltage, callback = None):
        anim = self.voltage_animation(voltage)
        now = time.ticks_ms()
        for i, l in enumerate(self.vehicle.lights):
            l.animate(anim, now = now, callback = callback if i == 0 else None)

    def start(self):
        for l in self.vehicle.lights:
            l.set_level(0)
        self.position = 0
        if self.vehicle.voltage is not None:
            self.do_voltage_animation(self.vehicle.voltage//self.vehicle.cells)

