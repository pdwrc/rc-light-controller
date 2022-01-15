from light import Animation
from button import ButtonEvent

class Telemetry:

    def __init__(self, vehicle):
        self.vehicle = vehicle


    def click(self, event, count = None):
        if self.vehicle.voltage is None:
            return False
        if event == ButtonEvent.SHORT_CLICK:
            for l in self.vehicle.lights:
                l.set_level(0)
                l.animate(((0,0),))
            if self.position >= 1:
                return False
            self.position += 1
            self.do_voltage_animation(self.vehicle.low_voltage//6)
        return True

    def voltage_animation(self, voltage):
        values = list((voltage // div) % 10 for div in (100, 10 ,1))
        a = []
        for v in values:
            a.append(((0,750),))
            a.append(Animation.multi_flash(v, on = 250, off = 250))
        a.append(((0,750),))
        return Animation.join(*a)

    def do_voltage_animation(self, voltage):
        anim = self.voltage_animation(voltage)
        for l in self.vehicle.lights:
            l.animate(anim)

    def start(self):
        self.position = 0
        if self.vehicle.voltage is not None:
            self.do_voltage_animation(self.vehicle.voltage//6)

