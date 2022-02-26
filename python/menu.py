from button import ButtonEvent
import light
from config import config, PWMMode, BrakeMode
import time
from animation import SimpleAnimation, BreatheAnimation

class MenuItem:

    def __init__(self, menu, light = None):
        self.light = light
        self.menu = menu

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(50, menu = True)

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
#        self.update(initial_value)

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
            self.level = ((self.level // 20) * 20 + 20) % 120
            self.update(self.level)
        return True

    def animate(self, light = None, now = None):
        pass

    def animate_all(self):
        now = time.ticks_ms()
        for l in self.menu.vehicle.all_lights:
            self.animate(l, now)

    def activate(self):
        self.animate_all()

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
        self.cur_fadespeed = config.fade_speed

    def update(self, level):
        self.cur_fadespeed = level/3;

    def animate(self, l, now = None):
        animation = SimpleAnimation.faded_flash(100, 0, 750, self.cur_fadespeed)
        l.animate(animation, callback = self.animate, now = now, menu = True)

    def save(self, level):
        config.fade_speed = self.cur_fadespeed

class AdjustBreatheTimeMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu):
        super().__init__(menu, None, config.breathe_time)
        self.cur_breathetime = config.breathe_time;

    def update(self, level):
        self.cur_breathetime = (level * 50) + 500;
        # Restart animation
        self.animate_all()

    def animate(self, l, now = None):
        l.animate(BreatheAnimation(self.cur_breathetime, config.breathe_gap, off_brightness = config.breathe_min_brightness), callback = self.animate, now = now, menu = True)

    def save(self, level):
        config.breathe_time = self.cur_breathetime

class AdjustBreatheGapMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu):
        super().__init__(menu, None, config.breathe_gap)
        self.cur_breathegap = config.breathe_gap;

    def update(self, level):
        self.cur_breathegap = (level * 50) + 500;
        # Restart animation
        self.animate_all()

    def animate(self, l, now = None):
        l.animate(BreatheAnimation(config.breathe_time, self.cur_breathegap), callback = self.animate, now = now, menu = True)

    def save(self, level):
        config.breathe_gap = self.cur_breathegap

class MultiSelectMenuItem(MenuItem):

    def __init__(self, menu, obj, prop, values):
        super().__init__(menu)
        self.prop = prop
        self.values = values
        self.obj = obj
        try:
            self.cur_value = values.index(getattr(obj, prop))
        except ValueError:
            self.cur_value = values[0]

    def update(self):
        for l in self.menu.vehicle.all_lights:
            l.set_level(100 * self.cur_value / len(self.values), menu = True)

    def activate(self):
        self.update()

    def click(self, event):
        if event == ButtonEvent.SHORT_CLICK:
            self.cur_value = (self.cur_value + 1) % len(self.values)
            print("Menu: %s Value %s" % (self.prop, self.values[self.cur_value]))
            self.update()
        if event == ButtonEvent.LONG_CLICK:
            setattr(self.obj, self.prop, self.values[self.cur_value])
            return False
        return True

class ToggleMenuItem(MultiSelectMenuItem):

    def __init__(self, menu, obj, prop):
        super().__init__(menu, obj, prop, [False, True])

class SteeringThresholdMenuItem(MenuItem):

    def __init__(self, menu):
        super().__init__(menu)

    def click(self, event):
        if event == ButtonEvent.LONG_CLICK:
            pos = self.menu.vehicle.steering.position
            if pos is not None:
                ths = abs(pos)
                if ths > 20:
                    config.steering_threshold = ths
                    print("Updating steering threshold to %d" % ths)
            return False
        return True

class Menu:

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.menu = SubMenu(self)
        self.menu.add(QuitMenu(self))
        self.menu.add(SubMenu(self, (
                QuitMenu(self),
                MultiSelectMenuItem(self, config, "pwm_mode", [PWMMode.SW_TH, PWMMode.TH_ST]),
                MultiSelectMenuItem(self, config, "pwm_brake_mode", [BrakeMode.SIMPLE, BrakeMode.SMART, BrakeMode.LIFT_OFF_DELAY]),
                AdjustFadeSpeedMenuItem(self),
                ToggleMenuItem(self, config, "use_handbrake"),
                SteeringThresholdMenuItem(self),
                SubMenu(self, (
                    QuitMenu(self),
                    MultiSelectMenuItem(self, config, "sleep_delay", [0, 5, 10, 30, 60]),
                    ToggleMenuItem(self, config, "sleep_when_lights_on"),
                    AdjustBreatheTimeMenuItem(self),
                    AdjustBreatheGapMenuItem(self),
                    MultiSelectMenuItem(self, config, "breathe_min_brightness", [0, 10, 20, 30, 50]),
                ))
            )
        ))
        for l in self.vehicle.lights:
            submenu = SubMenu(self, (
                QuitMenu(self),
                AdjustLightLevelMenuItem(self, l, "mode1"),
                AdjustLightLevelMenuItem(self, l, "mode2"),
                AdjustLightLevelMenuItem(self, l, "brake"),
                AdjustLightLevelMenuItem(self, l, "flash"),
                AdjustLightLevelMenuItem(self, l, "turn_left"),
                AdjustLightLevelMenuItem(self, l, "turn_right"),
                AdjustLightLevelMenuItem(self, l, "breathe"),
            ), light = l)
            self.menu.add(submenu)

    def start(self):
        self.menu_pos = 0
        self.menu_depth = 0 
        for l in self.vehicle.all_lights:
            l.animate(SimpleAnimation.multi_flash(1), menu = True)
        self.menu_stack = [(self.menu, 0)]
        self.clear_all()

    def adjust_level(self):
        pass

    def flash_all(self, n):
        for l in self.vehicle.all_lights:
            l.animate(SimpleAnimation.multi_flash(n), menu = True)

    def clear_all(self):
        for l in self.vehicle.all_lights:
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
                elif isinstance(item, (LevelAdjusterMenuItem, MultiSelectMenuItem, SteeringThresholdMenuItem)):
                    self.menu_stack.append((item, self.menu_pos))
                    item.activate()
                if type(item) == QuitMenu:
                    if not self.go_up():
                        return False
            print("Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))
        elif isinstance(cur_menu, (LevelAdjusterMenuItem, MultiSelectMenuItem, SteeringThresholdMenuItem)):
            if not cur_menu.click(event):
                self.go_up()
            print("Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))

        return True

    def level_setting(self, level):
        (cur_menu, n) = self.menu_stack[-1]
        cur_menu.level_setting(level)
