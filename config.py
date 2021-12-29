import json
import os
import vehicle

class Config:

    def __init__(self, data):

        self.lights = []
        lights = data.get("lights")
        if lights is not None:
            self.lights = [ vehicle.Light(x.get("pin"), x.get("off"), x.get("on"), x.get("brake")) for x in lights ]
        else:
            self.lights = [
                vehicle.Light(14, off = 0, on = 100),
                vehicle.Light(16, off = 10, on = 100, flash = 100),
                vehicle.Light(18, on = 40, brake = 90)
                ]

        self.primary_button_channel = data.get("button_channel", 8)
        self.primary_button_reverse = data.get("button_reverse", False)
        self.level_channel = data.get("level_channel", 6)
        self.level_channel_min = data.get("level_channel_min", 11000)
        self.level_channel_max = data.get("level_channel_min", 43000)


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
        data["primary_button_channel"] = self.primary_button_channel
        data["primary_button_reverse"] = self.primary_button_reverse

        with open("config.json", "w") as fout:
            json.dump(data, fout)


