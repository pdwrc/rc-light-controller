from button import ButtonEvent
import light
from config import config
import time

class MenuItem:

    def __init__(self, menu, light = None):
        self.light = light
        self.menu = menu

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(50)

    def activate(self):
        pass
    
    def level_setting(self, level):
        pass

class QuitMenu(MenuItem):
    pass

class SubMenu(MenuItem):
    
    def __init__(self, menu, items = None, light = None):
        super().__init__(menu, light)
        if items is not None:
            self.items = items
        else:
            self.items = []

    def add(self, item):
        self.items.append(item)


    @property
    def length(self):
        return len(self.items)


class LevelAdjusterMenuItem(MenuItem):

    def __init__(self, menu, light, initial_value):
        super().__init__(menu, light)
        self.level = initial_value
        self.last_input_level = None
        self.update(initial_value)

    def level_setting(self, level):
        # Only adjust the level if it's changed, so we don't override the
        # brightness cycle
        if self.last_input_level is not None and level != self.last_input_level:
            self.level = level
            self.update(level)
        self.last_input_level = level

    def click(self, event):
        if event == ButtonEvent.LONG_CLICK:
            self.save(self.level)
            return False
        elif event == ButtonEvent.SHORT_CLICK:
            self.level = (self.level + 20) % 120
            self.update(self.level)
        return True

class AdjustLightLevelMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu, light, state):
        super().__init__(menu, light, getattr(light.config, state))
        self.state = state

    def update(self, level):
        self.light.set_level(level)

    def save(self, level):
        setattr(self.light.config, self.state, level)

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(getattr(self.light.config, self.state, 0))

class AdjustFadeSpeedMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu):
        super().__init__(menu, None, config.fade_speed)

    def update(self, level):
        self.cur_fadespeed = level/3;

    def animate(self, l, now = None):
        flash_length = 5*self.cur_fadespeed
        animation = light.Animation.join(
                light.Animation.fade(0,100,self.cur_fadespeed), 
                ((100,0), (100, 250-flash_length)), 
                light.Animation.fade(100,0,self.cur_fadespeed), 
                ((0,0),(0, 1000-flash_length))
                )
        l.animate(animation, callback = self.animate, now = now)

    def save(self, level):
        config.fade_speed = self.cur_fadespeed

    def activate(self):
        now = time.ticks_ms()
        for l in self.menu.vehicle.lights:
            self.animate(l, now)

class ToggleMenuItem(MenuItem):

    def __init__(self, menu, obj, prop):
        super().__init__(menu)
        self.obj = obj
        self.prop = prop
        self.cur_value = getattr(obj, prop)

    def update(self):
        for l in self.menu.vehicle.lights:
            l.set_level(50 if self.cur_value else 0)

    def activate(self):
        self.update()

    def click(self, event):
        if event == ButtonEvent.SHORT_CLICK:
            self.cur_value = not self.cur_value
            self.update()
        if event == ButtonEvent.LONG_CLICK:
            setattr(self.obj, self.prop, self.cur_value)
            return False
        return True

class Menu:

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.menu = SubMenu(self)
        self.menu.add(QuitMenu(self))
        for l in self.vehicle.lights:
            submenu = SubMenu(self, (
                QuitMenu(self),
                AdjustLightLevelMenuItem(self, l, "mode1"),
                AdjustLightLevelMenuItem(self, l, "mode2"),
                AdjustLightLevelMenuItem(self, l, "brake"),
                AdjustLightLevelMenuItem(self, l, "flash"),
            ), light = l)
            self.menu.add(submenu)
        self.menu.add(AdjustFadeSpeedMenuItem(self))
        self.menu.add(ToggleMenuItem(self, config, "use_handbrake"))

    def start(self):
        self.menu_pos = 0
        self.menu_depth = 0 
        for l in self.vehicle.lights:
            l.animate(light.Animation.multi_flash(1))
        self.menu_stack = [(self.menu, 0)]
        self.clear_all()

    def adjust_level(self):
        pass

    def flash_all(self, n):
        for l in self.vehicle.lights:
            l.animate(light.Animation.multi_flash(n))

    def clear_all(self):
        for l in self.vehicle.lights:
            l.set_level(0)

    def go_up(self):
        (submenu, self.menu_pos) = self.menu_stack.pop()
        if len(self.menu_stack) == 0:
            config.save()
            return False
        else:
            self.flash_all(self.menu_pos + 1)
            self.menu_stack[-1][0].items[self.menu_pos].select()
        return True

    def click(self, event):
        (cur_menu, n) = self.menu_stack[-1]

        if (type(cur_menu) == SubMenu):
            if event == ButtonEvent.SHORT_CLICK:
                self.menu_pos = (self.menu_pos + 1) % cur_menu.length
                item = cur_menu.items[self.menu_pos]
                self.flash_all(self.menu_pos + 1)
                item.select()
            if event == ButtonEvent.LONG_CLICK:
                item = cur_menu.items[self.menu_pos]
                if type(item) == SubMenu:
                    self.menu_stack.append((item, self.menu_pos))
                    self.menu_pos = 0
                    self.flash_all(self.menu_pos + 1)
                    item.items[0].select()
                elif isinstance(item, (LevelAdjusterMenuItem, ToggleMenuItem)):
                    self.menu_stack.append((item, self.menu_pos))
                    item.activate()
                if type(item) == QuitMenu:
                    if not self.go_up():
                        return False
            print("Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))
        elif isinstance(cur_menu, (LevelAdjusterMenuItem, ToggleMenuItem)):
            if not cur_menu.click(event):
                self.go_up()
            print("Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))

        return True

    def level_setting(self, level):
        (cur_menu, n) = self.menu_stack[-1]
        cur_menu.level_setting(level)
