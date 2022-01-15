import json
import os

class LightConfig:

    def __init__(self, pin, mode1, mode2, brake = 0, flash = 0):
        self.pin = pin
        self.mode1 = mode1
        self.mode2 = mode2
        self.brake = brake
        self.flash = flash

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
            self.lights = [
                LightConfig(14, 20, 60, flash = 100),
                LightConfig(16, 30, 90),
                LightConfig(18, 30, 70, brake = 90)
                ]

        self.primary_button_channel = data.get("primary_button_channel", 8)
        self.primary_button_reverse = data.get("primary_button_reverse", False)
        self.handbrake_button_channel = data.get("handbrake_button_channel", 8)
        self.handbrake_button_reverse = data.get("handbrake_button_reverse", True)
        self.level_channel = data.get("level_channel", 6)
        self.level_channel_min = data.get("level_channel_min", 11000)
        self.level_channel_max = data.get("level_channel_min", 43000)
        self.fade_speed = data.get("fade_speed", 18)
        self.use_handbrake = data.get("use_handbrake", True)

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
        for x in ("primary_button_channel", "primary_button_reverse", "handbrake_button_channel", "handbrake_button_reverse", "fade_speed", "use_handbrake"):
            data[x] = getattr(self, x)

        with open("config.json", "w") as fout:
            json.dump(data, fout)
        print("config saved")

        return


config = Config.load()

