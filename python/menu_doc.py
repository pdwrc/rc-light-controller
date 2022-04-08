import menu
import config
from light import Light
from vehicle import Vehicle

class DummyVehicle:

    def __init__(self, config):
        self.lights = [Light(c, channel = n) for (n, c) in enumerate(config.lights)]


def menu_walk(m, level = 0):
    for (n, item) in enumerate(m.items):
        if item.title is None:
            print(type(item))
        else:
            print("    " * level + "* %d\\. " % (n+1) +  item.title)
        if isinstance(item, menu.SubMenu):
            if item.repeat_text is None:
                menu_walk(item, level = level + 1)
            else:
                print("    " * (level+1) + "_%s_" % item.repeat_text)

vehicle = Vehicle(config.config)
m = menu.Menu(vehicle)
menu_walk(m.menu)


