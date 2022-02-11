import json
import os

from pins import Pins

class LightConfig:

    def __init__(self, pin, mode1, mode2, brake = 0, flash = 0, menu = 50):
        self.pin = pin
        self.mode1 = mode1
        self.mode2 = mode2
        self.brake = brake
        self.flash = flash
        self.menu = menu

    def as_dict(self):
        return {
            "pin": self.pin,
            "mode1": self.mode1,
            "mode2": self.mode2,
            "flash": self.flash,
            "brake": self.brake
        }


class Config:

    def __init__(self, data):

        self.lights = []
        lights = data.get("lights")
        if lights is not None:
            self.lights = [ LightConfig(x.get("pin"), x.get("mode1", 0), x.get("mode2", 100), x.get("brake", 0), x.get("flash", 0)) for x in lights ]
        else:
            for pin in Pins.OUTPUTS:
                self.lights.append(LightConfig(pin, 20, 100))

            # Make the last light a brake light
            self.lights[-1].brake = 100
            self.lights[-1].mode2 = 00

        self.primary_button_channel = data.get("primary_button_channel", 8)
        self.primary_button_reverse = data.get("primary_button_reverse", False)
        self.handbrake_button_channel = data.get("handbrake_button_channel", 8)
        self.handbrake_button_reverse = data.get("handbrake_button_reverse", True)
        self.level_channel = data.get("level_channel", 6)
        self.level_channel_min = data.get("level_channel_min", 11000)
        self.level_channel_max = data.get("level_channel_min", 43000)
        self.fade_speed = data.get("fade_speed", 18)
        self.use_handbrake = data.get("use_handbrake", True)
        self.throttle_channel = data.get("throttle_channel",1)
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
        for x in ("primary_button_channel", "primary_button_reverse", "handbrake_button_channel", "handbrake_button_reverse", "fade_speed", "use_handbrake", "throttle_channel"):
            data[x] = getattr(self, x)

        with open("config.json", "w") as fout:
            json.dump(data, fout)
        print("config saved")

        return


config = Config.load()

