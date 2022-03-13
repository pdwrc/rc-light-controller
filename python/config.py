import json
import os

from pins import Pins

class RCMode:
    PWM = 0
    SMART = 1

class BrakeMode:
    SIMPLE = 0
    SMART = 1
    LIFT_OFF_DELAY = 2

class ButtonMode:
    NONE = 0
    BRAKE = 1
    FLASH = 2
    EMERGENCY_TOGGLE = 3

class LightConfig:

    def __init__(self, pin, mode1, mode2, brake = 0, flash = 0, breathe = 0, turn_left = 0, turn_right = 0, emergency1 = 0, emergency2 = 0, menu = 50):
        self.pin = pin
        self.mode1 = mode1
        self.mode2 = mode2
        self.brake = brake
        self.flash = flash
        self.breathe = breathe
        self.turn_left = turn_left
        self.turn_right = turn_right
        self.emergency1 = emergency1
        self.emergency2 = emergency2
        self.menu = menu

    def as_dict(self):
        return {
            "pin": self.pin,
            "mode1": self.mode1,
            "mode2": self.mode2,
            "flash": self.flash,
            "brake": self.brake,
            "breathe": self.breathe,
            "turn_left": self.turn_left,
            "turn_right": self.turn_right,
            "emergency1": self.emergency1,
            "emergency2": self.emergency2,
        }

class PWMMode:
    SW_TH = 0
    TH_ST = 1

class Config:

    def __init__(self, data):

        self.lights = []
        lights = data.get("lights")
        if lights is not None:
            self.lights = [ LightConfig(
                x.get("pin"), 
                x.get("mode1", 0), 
                x.get("mode2", 100), 
                x.get("brake", 0), 
                x.get("flash", 0), 
                x.get("breathe",0),
                x.get("turn_left",0),
                x.get("turn_right",0),
                x.get("emergency1",0),
                x.get("emergency2",0),
            ) for x in lights ]
        else:
            for pin in Pins.OUTPUTS:
                self.lights.append(LightConfig(pin, 20, 100))

            # First light should breathe
            self.lights[0].breathe = 40

            # Second light should flash
            self.lights[1].flash = 100

            # Make the last light a brake light
            self.lights[-1].brake = 100
            self.lights[-1].mode2 = 20

        self.pwm_mode = data.get("pwm_mode", PWMMode.TH_ST)
        self.primary_button_channel = data.get("primary_button_channel", 8)
        self.primary_button_reverse = data.get("primary_button_reverse", False)
        self.handbrake_button_channel = data.get("handbrake_button_channel", 8)
        self.handbrake_button_reverse = data.get("handbrake_button_reverse", True)
        self.level_channel = data.get("level_channel", 6)
        self.level_channel_min = data.get("level_channel_min", 1250)
        self.level_channel_max = data.get("level_channel_max", 1750)
        self.sleep_delay = data.get("sleep_delay", 5)
        self.sleep_when_lights_on = data.get("sleep_when_lights_on", False)
        self.breathe_min_brightness = data.get("breathe_min_brightness", 0)
        self.breathe_time = data.get("breathe_time", 4000)
        self.breathe_gap = data.get("breathe_gap", 2000)
        self.fade_speed = data.get("fade_speed", 18)
        self.secondary_button_mode = data.get("secondary_button_mode", ButtonMode.NONE)
        self.steering_threshold = data.get("steering_threshold", 100)
        self.pwm_brake_mode = data.get("pwm_brake_mode", BrakeMode.SMART)
        self.hardware_button_pin = Pins.BUTTON
        self.input_pins = Pins.INPUTS
        self.status_led_pins = Pins.STATUS_LEDS

    def load():
        try:
            with open("config.json") as fin:
                return Config(json.load(fin))
        except:
            new_config = Config({})
            return new_config

    def save(self):
        data = {}
        data["lights"] = [ light.as_dict() for light in self.lights ]
        for x in ("primary_button_channel", "primary_button_reverse", "handbrake_button_channel", "handbrake_button_reverse", 
                "fade_speed", "secondary_button_mode", "pwm_mode", "breathe_time", "breathe_gap", "sleep_delay",
                "sleep_when_lights_on", "breathe_min_brightness", "steering_threshold", "pwm_brake_mode"):
            data[x] = getattr(self, x)

        with open("config.json", "w") as fout:
            json.dump(data, fout)
        print("config saved")

        return

    def channel_map(self, mode, vehicle):
        cm = {}
        if mode == RCMode.SMART:
            cm[(self.primary_button_channel, self.primary_button_reverse)] = vehicle.primary_button
            cm[(self.handbrake_button_channel, self.handbrake_button_reverse)] = vehicle.secondary_button
            cm[(1, False)] = vehicle.throttle
            cm[(4, False)] = vehicle.steering
        else:
            if self.pwm_mode == PWMMode.SW_TH:
                cm[1, False] = vehicle.primary_button
                cm[1, True] = vehicle.secondary_button
                if len(self.input_pins) > 1:
                    cm[2, False] = vehicle.throttle
            elif self.pwm_mode == PWMMode.TH_ST:
                cm[1, False] = vehicle.throttle
                if len(self.input_pins) > 1:
                    cm[2, False] = vehicle.steering

        return cm
        

config = Config.load()

