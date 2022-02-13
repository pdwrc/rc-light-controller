try:
    from machine import Pin, PWM
except ModuleNotFoundError:
    from machine_mock import Pin, PWM

from button import ButtonEvent, Button
from channel import Channel
import menu
import telemetry
import time
from light import LightState, Light
from animation import SimpleAnimation, BreatheAnimation
from config import LightConfig, RCMode, config
from laststate import LastState


class Vehicle:

    def __init__(self, config):
        self.moving = False
        self.light_state = LastState.load()
        self.brakes_on = False
        self.lights_flash = False
        self.lights = [Light(c) for c in config.lights]
        self.in_menu = False
        self.in_telemetry = False
        self.menu = menu.Menu(self)
        self.telemetry = telemetry.Telemetry(self)
        self.config = config
        self.handbrake = False
        self.voltage = None
        self.low_voltage = None
        self.cells = None
        self.reversing = False
        self.esc_braking = False
        self.quick_brake = None
        self.status_led = Light(LightConfig(config.status_led_pins, 0, 100, menu = 100), no_pwm = True)

        self.throttle = Channel()
        self.steering = Channel()
        self.primary_button = Button(self.primary_click)
        self.secondary_button = Button(self.handbrake_click)
        self.mode = None

        self.last_movement = time.ticks_ms()
        self.breathing = None

    def primary_click(self, event, count = None):
        if self.in_menu:
            self.in_menu = self.menu.click(event)
        if self.in_telemetry:
            self.in_telemetry = self.telemetry.click(event, count)
            print("In telemetry: " + str(self.in_telemetry))
        elif not self.moving:
            if event == ButtonEvent.SHORT_CLICK:
                if self.light_state < LightState.HIGH:
                    self.light_state += 1
                else:
                    self.light_state = LightState.LOW
                self.update()
                LastState.save(self.light_state)
            elif event == ButtonEvent.LONG_CLICK:
                self.light_state = LightState.OFF
                LastState.save(self.light_state)
            elif event == ButtonEvent.EXTRA_LONG_HOLD and count <= 2:
                # Button has been held down for a long time, but has not been released yet
                # Flash up to two times (telemetry then menu)
                # Turn off the lights so they don't come back on between
                # animations.
                for l in self.all_lights:
                    l.set_level(0)
                    l.animate(SimpleAnimation.multi_flash(1))
            elif event == ButtonEvent.EXTRA_LONG_CLICK:
                if count == 1:
                    self.telemetry.start()
                    self.in_telemetry = True
                elif count > 1:
                    self.menu.start()
                    self.in_menu = True
            if self.breathing:
                self.stop_breathing()
        else:
            # moving
            if event == ButtonEvent.PRESS:
                self.lights_flash = True
                self.update()

        # Moving or stopped
        if event == ButtonEvent.RELEASE and self.lights_flash:
            self.lights_flash = False
            self.update()

        self.last_movement = time.ticks_ms()

    def handbrake_click(self, event, count = None):
        if event == ButtonEvent.PRESS:
            self.handbrake = True
            self.update()
        elif event == ButtonEvent.RELEASE:
            self.handbrake = False
            self.update()
        print("Handbrake %s" % str(self.handbrake))

    def level_setting(self, level):
        if self.in_menu:
            self.menu.level_setting(level)

    def calculate_cells(self, voltage):
        for c in reversed([1,2,3,4,6,8]):
            if voltage >= 316 * c:
                return c
        return None

    def set_state(self, moving, brakes, voltage):

        if moving and not self.moving:
            # Just started moving
            self.reversing = self.throttle and self.throttle.reverse
            if self.reversing:
                print("Reversing")
            else:
                print("Forwards")

        self.moving = moving
        self.esc_braking = brakes

        if self.voltage is None and voltage is not None:
            self.cells = self.calculate_cells(voltage)
            print("%d cells" % self.cells)
        self.voltage = voltage
        if self.low_voltage is None or voltage < self.low_voltage:
            self.low_voltage = voltage

    def update_brake(self):
        if self.mode == RCMode.PWM:
            self.brakes_on = self.throttle.reverse
        else:
            # Quick brake shows the brake light as soon as the throttle is
            # reversed for up to 0.25s if we're confident that we're moving
            # forwards.  This avoids the short delay from waiting for telemetry to
            # detect braking.
            if self.throttle.reverse:
                if self.quick_brake is None and not self.reversing and self.moving:
                    self.quick_brake = time.ticks_ms() 
                    print("Quick brake")
            else:
                # Reset quick brake if throttle neutral
                self.quick_brake = None

            self.brakes_on = self.esc_braking or (self.quick_brake is not None and time.ticks_ms() - self.quick_brake < 250)

    def stop_breathing(self):
        for l in self.lights:
            l.animate(None)
        self.breathing = False

    def update_breathe(self):
        if self.moving or not self.throttle.neutral or not self.steering.neutral:
            self.last_movement = time.ticks_ms()
            if self.breathing:
                self.stop_breathing()

        now = time.ticks_ms()
        if now - self.last_movement > 3000 and not self.breathing and not self.in_menu and not self.in_telemetry:
            self.breathing = True
            for l in self.lights:
                if l.config.breathe > 0:
                    l.animate(BreatheAnimation(config.breathe_time, config.breathe_gap, brightness = l.config.breathe), now = now, loop = True)



    def update(self):
        if (self.moving or not self.throttle.neutral) and self.in_menu:
            self.config.save()
            self.in_menu = False

        self.update_brake()
        self.update_breathe()

        if self.moving:
            self.in_telemetry = False

        now = time.ticks_ms()

        for light in self.lights:
            if self.in_menu or self.in_telemetry:
                light.tick(now)
            else:
                light.update(now, self.light_state, self.brakes_on or (self.handbrake and self.config.use_handbrake), self.lights_flash)

        self.status_led.tick(now)

    @property
    def all_lights(self):
        return self.lights + [self.status_led]

