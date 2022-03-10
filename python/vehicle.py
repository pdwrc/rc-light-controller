try:
    from machine import Pin, PWM
except ModuleNotFoundError:
    from machine_mock import Pin, PWM

from button import ButtonEvent, Button
from channel import Channel, SteeringChannel
import menu
import telemetry
import time
from light import LightState, Light
from animation import SimpleAnimation, BreatheAnimation, EmergencyFlash
from config import LightConfig, RCMode, config, BrakeMode, ButtonMode
from laststate import LastState


class Turn:
    NONE = 0
    LEFT = 1
    RIGHT = -1

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
        self.voltage = None
        self.low_voltage = None
        self.cells = None
        self.reversing = False
        self.esc_braking = False
        self.quick_brake = None
        self.status_led = Light(LightConfig(config.status_led_pins, 0, 100, menu = 100), no_pwm = True)

        self.throttle = Channel()
        self.steering = SteeringChannel()
        self.primary_button = Button(self.primary_click)
        self.secondary_button = Button(self.secondary_click)
        self.mode = None

        self.last_movement = time.ticks_ms()
        self.sleeping = False
        self.turning = Turn.NONE
        self.startup = True
        self.braked_once = False
        self.timed_brake = 0
        self.emergency = True

    def primary_click(self, event, count = None):
        if self.in_menu:
            self.in_menu = self.menu.click(event)
            if not self.in_menu:
                self.min_animation_priority(None)
        elif self.in_telemetry:
            self.in_telemetry = self.telemetry.click(event, count)
            print("In telemetry: " + str(self.in_telemetry))
        elif not self.moving:
            if event == ButtonEvent.SHORT_CLICK:
                if self.light_state < LightState.HIGH:
                    self.light_state += 1
                else:
                    self.light_state = LightState.LOW
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
                    self.min_animation_priority(0)
            if self.sleeping:
                self.stop_sleeping()
        else:
            # moving
            if event == ButtonEvent.PRESS:
                self.lights_flash = True

        # Moving or stopped
        if event == ButtonEvent.RELEASE and self.lights_flash:
            self.lights_flash = False

        self.last_movement = time.ticks_ms()

    def startup_complete(self):
        self.last_movement = time.ticks_ms()
        self.startup = False

    def secondary_click(self, event, count = None):
        pass

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
            if config.pwm_brake_mode == BrakeMode.SIMPLE:
                self.brakes_on = self.throttle.reverse
            elif config.pwm_brake_mode == BrakeMode.SMART:
                if self.throttle.reverse and not self.braked_once:
                    self.brakes_on = True
                else:
                    if not self.throttle.reverse and self.brakes_on:
                        self.braked_once = True
                    elif self.throttle.forward:
                        self.braked_once = False
                    self.brakes_on = False
            elif config.pwm_brake_mode == BrakeMode.LIFT_OFF_DELAY:
                if self.throttle.neutral:
                    if self.timed_brake is None:
                        self.timed_brake = time.ticks_ms()
                        self.brakes_on = True
                    elif time.ticks_ms() - self.timed_brake < 1000:
                        self.brakes_on = True
                    else:
                        self.brakes_on = False
                else:
                    self.brakes_on = False
                    self.timed_brake = None

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

    def update_steering(self):
        now = time.ticks_ms()
        if self.steering.right:
            if self.turning != Turn.RIGHT:
                for l in self.lights:
                    if l.config.turn_right > 0:
                        l.animate(SimpleAnimation.faded_flash(l.config.turn_right, 0, 500), now = now, loop = True)
                        self.turning = Turn.RIGHT
                    else: 
                        l.animate(None)
        elif self.steering.left:
            if self.turning != Turn.LEFT:
                for l in self.lights:
                    if l.config.turn_left > 0:
                        l.animate(SimpleAnimation.faded_flash(l.config.turn_left, 0, 500), now = now, loop = True)
                        self.turning = Turn.LEFT
                    else: 
                        l.animate(None)
        elif self.turning != Turn.NONE:
            for l in self.lights:
                l.animate(None)
            self.turning = Turn.NONE


    def stop_sleeping(self):
        for l in self.lights:
            l.animate(None)
        self.min_animation_priority(None)
        self.sleeping = False

    def min_animation_priority(self, priority):
        for l in self.lights:
            l.min_animation_priority = priority


    def update_breathe(self):
        active = (self.moving or not self.throttle.neutral or not self.steering.neutral or self.brakes_on
                or self.in_menu or self.in_telemetry or self.primary_button.is_pressed or self.secondary_button.is_pressed)

        if active:
            self.last_movement = time.ticks_ms()
            if self.sleeping:
                self.stop_sleeping()

        now = time.ticks_ms()
        if (now - self.last_movement > config.sleep_delay*1000 and not self.sleeping 
            and not active
            and (self.light_state == LightState.OFF or config.sleep_when_lights_on)):
            self.sleeping = True
            for l in self.lights:
                if l.config.breathe > 0:
                    l.animate(BreatheAnimation(config.breathe_time, config.breathe_gap, brightness = l.config.breathe, off_brightness = config.breathe_min_brightness), now = now, loop = True)
                else:
                    l.set_level(0)
            self.min_animation_priority(0)

    def update(self):
        if not self.startup:
            if (self.moving or not self.throttle.neutral) and self.in_menu:
                self.config.save()
                self.in_menu = False
                self.min_animation_priority(None)

            self.update_brake()
            self.update_breathe()
            self.update_steering()

            if self.moving:
                self.in_telemetry = False

        now = time.ticks_ms()

        flash = self.lights_flash or (config.secondary_button_mode == ButtonMode.FLASH and self.secondary_button.is_pressed)
        handbrake = config.secondary_button_mode == ButtonMode.BRAKE and self.secondary_button.is_pressed
        for light in self.lights:
            if self.in_menu or self.in_telemetry or self.sleeping or self.startup:
                light.tick(now)
            else:
                light.update(now, self.light_state, self.brakes_on or handbrake, flash, self.emergency)

        self.status_led.tick(now)

    @property
    def all_lights(self):
        return self.lights + [self.status_led]

