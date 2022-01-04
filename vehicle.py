try:
    from machine import Pin, PWM
except ModuleNotFoundError:
    from machine_mock import Pin, PWM

from button import ButtonEvent
import menu
import time

import config

class LightState:
    OFF = 0
    LOW = 1
    HIGH = 2

class Vehicle:

    def __init__(self, config):
        self.moving = False
        self.throttle = 0
        self.light_state = LightState.OFF
        self.brakes_on = False
        self.lights_flash = False
        self.lights = config.lights
        self.in_menu = False
        self.menu = menu.Menu(self)
        self.config = config
        self.handbrake = False


    def primary_click(self, event):
        if self.in_menu:
            self.in_menu = self.menu.click(event)
        elif not self.moving:
            if event == ButtonEvent.SHORT_CLICK:
                if self.light_state < LightState.HIGH:
                    self.light_state += 1
                else:
                    self.light_state = LightState.LOW
                self.update()
            elif event == ButtonEvent.LONG_CLICK:
                self.light_state = LightState.OFF
            elif event == ButtonEvent.EXTRA_LONG_CLICK:
                self.menu.start()
                self.in_menu = True
        else:
            # moving
            if event == ButtonEvent.PRESS:
                self.lights_flash = True
                self.update()

        # Moving or stopped
        if event == ButtonEvent.RELEASE and self.lights_flash:
            self.lights_flash = False
            self.update()

    def handbrake_click(self, event):
        if event == ButtonEvent.PRESS:
            self.handbrake = True
            self.update()
        elif event == ButtonEvent.RELEASE:
            self.handbrake = False
            self.update()

    def level_setting(self, level):
        if self.in_menu:
            self.menu.level_setting(level)

    def set_state(self, moving, brakes):
        self.moving = moving
        self.brakes_on = brakes
        self.update()

    def update(self):
        if self.moving and self.in_menu:
            self.config.save()
            self.in_menu = False

        for light in self.lights:
            if self.in_menu:
                light.tick()
            else:
                light.update(self.light_state, self.brakes_on or self.handbrake, self.lights_flash)

        


