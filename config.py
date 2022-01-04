import json
import os
import vehicle
import light

class Config:

    _config = None

    def __init__(self, data):

        self.lights = []
        lights = data.get("lights")
        if lights is not None:
            self.lights = [ light.Light(x.get("pin"), x.get("off"), x.get("on"), x.get("brake"), x.get("flash")) for x in lights ]
        else:
            self.lights = [
                light.Light(14, off = 20, on = 60, flash = 100),
                light.Light(16, off = 30, on = 90),
                light.Light(18, off = 30, on = 70, brake = 90)
                ]

        self.primary_button_channel = data.get("primary_button_channel", 8)
        self.primary_button_reverse = data.get("primary_button_reverse", False)
        self.handbrake_button_channel = data.get("handbrake_button_channel", 8)
        self.handbrake_button_reverse = data.get("handbrake_button_reverse", True)
        self.level_channel = data.get("level_channel", 6)
        self.level_channel_min = data.get("level_channel_min", 11000)
        self.level_channel_max = data.get("level_channel_min", 43000)
        self.fade_speed = data.get("fade_speed", 18)

    def config():
        if Config._config is None:
            Config._config = Config.load()
        return Config._config

    def load():
        try:
            with open("config.json") as fin:
                return Config(json.load(fin))
        except:
            new_config = Config({})
            #new_config.save()
            return new_config

    def save(self):
        data = {}
        data["lights"] = [ light.as_dict() for light in self.lights ]
        for x in ("primary_button_channel", "primary_button_reverse", "handbrake_button_channel", "handbrake_button_reverse", "fade_speed"):
            data[x] = getattr(self, x)

        with open("config.json", "w") as fout:
            json.dump(data, fout)
        print("config saved")

        return

