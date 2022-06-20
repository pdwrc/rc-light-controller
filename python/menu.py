from button import ButtonEvent
import light
from config import config, PWMMode, BrakeMode, ButtonMode, EmergencyMode, LightStates, SleepWhenLightsOnMode, FadeTimeConfig, SleepDelayConfig, BreatheTimeConfig, BreatheGapConfig, SteeringThresholdConfig, BreatheMinimumBrightnessConfig, EmergencyFlashPeriodConfig, EmergencyFlashCountConfig, EmergencyFadeMode, ESCTemperatureAlarm, ESCTemperatureAlarmEnable
import time
from animation import SimpleAnimation, BreatheAnimation, FadedFlash, EmergencyFlash

class MenuItem:

    def __init__(self, menu, light = None):
        self.light = light
        self.menu = menu
        self.title = None

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(50, menu = True)

    def activate(self):
        pass
    
    def level_setting(self, level):
        pass

    def spec(self):
        return None


class QuitMenu(MenuItem):

    def __init__(self, menu, title = "(Go up)"):
        super().__init__(menu)
        self.title = title

class SubMenu(MenuItem):
    
    def __init__(self, menu, items = None, light = None, title="", config_path="None", repeat_text = None):
        super().__init__(menu, light)
        self.title = title
        if items is not None:
            self.items = items
        else:
            self.items = []
        self.config_path = config_path
        self.repeat_text = repeat_text

    def add(self, item):
        self.items.append(item)

    @property
    def length(self):
        return len(self.items)

    def spec(self):
        spec = {
            "title": self.title,
            "type": "section",
            "items": [],
            "config_path": self.config_path
        }
        if self.light is not None:
            spec['light'] = self.light.channel
        for item in self.items:
            s = item.spec()
            if s is not None:
                spec["items"].append(s)

        return spec

class LevelAdjusterMenuItem(MenuItem):

    def __init__(self, menu, light, initial_value, config_class = None):
        super().__init__(menu, light)
        self.level = initial_value
        self.last_input_level = None
        self.config_class = config_class
        if config_class is not None:
            self.title = config_class.title
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

    @property
    def min_value(self):
        return getattr(self.config_class, 'min_value', 0)

    @property
    def max_value(self):
        return getattr(self.config_class, 'max_value', 100)

    def spec(self):
        if self.config_class is None:
            return None
        return {
            'type': 'level',
            'name': self.config_class.name,
            'title': self.config_class.title,
            'description': self.config_class.description,
            'min': self.min_value,
            'max': self.max_value,
            'units': getattr(self.config_class, 'units', None)
        }

class GenericLevelAdjusterMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu, config, config_class):
        super().__init__(menu, None, getattr(config, config_class.name), config_class)
        self.config = config

    def update(self, level):
        self.level = int(self.min_value + (self.max_value - self.min_value) * level/100)

    def save(self, level):
        setattr(self.config, self.config_class.name, level)

class AdjustLightLevelMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu, light, state):
        super().__init__(menu, light, getattr(light.config, state.name))
        self.state = state
        self.title = self.state.title

    def update(self, level):
        self.light.set_level(level)

    def save(self, level):
        setattr(self.light.config, self.state.name, level)

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(getattr(self.light.config, self.state.name, 0))

    def spec(self):
        return {
            'type': 'light_level',
            'title': self.state.title,
            'description': self.state.description,
            'name': self.state.name,
            'light': self.light.channel
        }

class AdjustFadeSpeedMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu, config_class = None):
        super().__init__(menu, None, config.fade_time, config_class = FadeTimeConfig)
        self.cur_fade_time = config.fade_time

    def update(self, level):
        self.cur_fade_time = int(level*1.6)

    def animate(self, l, now = None):
        animation = FadedFlash(100, 0, 1500, self.cur_fade_time)
        l.animate(animation, callback = self.animate, now = now, menu = True)

    def save(self, level):
        config.fade_time = self.cur_fade_time

    def spec(self):
        spec = super().spec()
        spec['max'] = 250
        spec['units'] = 'ms'
        return spec
    
class AdjustEmergencyFlashPeriodMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu):
        super().__init__(menu, None, config.fade_time, config_class = EmergencyFlashPeriodConfig)
        self.cur_flash_period = config.emergency_flash_period

    def update(self, level):
        self.cur_flash_period = self.config_class.min_value + (level*(self.config_class.max_value - self.config_class.min_value))//100
        self.animate_all()

    def animate(self, l, now = None):
        l.animate(EmergencyFlash(100, 100, self.cur_flash_period, config.emergency_flashes_per_side, bool(config.emergency_fade)))

    def save(self, level):
        config.emergency_flash_period = self.cur_flash_period
        for l in self.menu.vehicle.all_lights:
            l.animate(None)

class AdjustBreatheTimeMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu):
        super().__init__(menu, None, config.breathe_time, config_class=BreatheTimeConfig)
        self.cur_breathetime = config.breathe_time;

    def update(self, level):
        self.cur_breathetime = (level * 50) + 500;
        # Restart animation
        self.animate_all()

    def animate(self, l, now = None):
        l.animate(BreatheAnimation(self.cur_breathetime, config.breathe_gap, off_brightness = config.breathe_min_brightness), callback = self.animate, now = now, menu = True)

    def save(self, level):
        config.breathe_time = self.cur_breathetime

    def spec(self):
        spec = super().spec()
        spec["min"] = 50
        spec["max"] = 6000
        spec["units"] = "ms"
        return spec

class AdjustBreatheGapMenuItem(LevelAdjusterMenuItem):

    def __init__(self, menu):
        super().__init__(menu, None, config.breathe_gap, config_class=BreatheGapConfig)
        self.cur_breathegap = config.breathe_gap;

    def update(self, level):
        self.cur_breathegap = (level * 50)
        # Restart animation
        self.animate_all()

    def animate(self, l, now = None):
        l.animate(BreatheAnimation(config.breathe_time, self.cur_breathegap), callback = self.animate, now = now, menu = True)

    def save(self, level):
        config.breathe_gap = self.cur_breathegap


class MultiSelectMenuItem(MenuItem):

    def __init__(self, menu, obj, prop, values, config_class = None):
        super().__init__(menu)
        self.prop = prop
        self.values = values
        self.obj = obj
        self.config_class = config_class

        if config_class is not None:
            self.title = config_class.title

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
            print("LOG Menu: %s Value %s" % (self.prop, self.values[self.cur_value]))
            self.update()
        if event == ButtonEvent.LONG_CLICK:
            setattr(self.obj, self.prop, self.values[self.cur_value])
            return False
        return True

    def spec(self):
        if self.config_class is None:
            return None
        return {
            'type': 'multi_select',
            'title': self.config_class.title,
            'description': self.config_class.description,
            'name': self.prop,
            'values': self.values,
            'labels': self.config_class.labels
        }

class HybridMenuItem(MultiSelectMenuItem):

    def __init__(self, menu, obj, prop, values, config_class = None, min_value = None, max_value = None, units = None):
        super().__init__(menu, obj, prop, values, config_class)
        if min_value is None:
            self.min_value = min(values)
        else:
            self.min_value = min_value
        if max_value is None:
            self.max_value = max(values)
        else:
            self.max_value = max_value
        self.units = units

    def spec(self):
        return {
            'type': 'level',
            'name': self.config_class.name,
            'title': self.config_class.title,
            'description': self.config_class.description,
            'min': self.min_value,
            'max': self.max_value,
            "units": self.units
        }


class ToggleMenuItem(MultiSelectMenuItem):

    def __init__(self, menu, obj, prop, config_class = None):
        super().__init__(menu, obj, prop, [0, 1], config_class = config_class)

class SteeringThresholdMenuItem(MenuItem):

    def __init__(self, menu):
        super().__init__(menu)
        self.config_class = SteeringThresholdConfig
        self.title = SteeringThresholdConfig.title

    def click(self, event):
        if event == ButtonEvent.LONG_CLICK:
            pos = self.menu.vehicle.steering.position
            if pos is not None:
                ths = abs(pos)
                if ths > 20:
                    config.steering_threshold = ths
                    print("LOG Updating steering threshold to %d" % ths)
            return False
        return True

    def spec(self):
        return {
            "type": "level",
            "min": 0,
            "max": 1000,
            "name": self.config_class.name,
            "title": self.config_class.title,
            "description": self.config_class.description,
        }

class EmergencyFlashCountMenuItem(MultiSelectMenuItem):

    def __init__(self, menu, obj, prop, config_class = None):
        super().__init__(menu, obj, prop, [1, 2, 3, 4, 5, 6], config_class = config_class)

    def update(self):
        for l in self.menu.vehicle.all_lights:
            l.set_level(100 * self.cur_value / len(self.values), menu = True)

    def activate(self):
        self.update()

class Menu:

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.menu = SubMenu(self, title="Configuration")
        self.menu.add(QuitMenu(self, title="Quit"))
        general_items = [
            QuitMenu(self)
        ]
        if len(config.input_pins) < 3:
            general_items.append(MultiSelectMenuItem(self, config, "pwm_mode", [PWMMode.SW_TH, PWMMode.TH_ST, PWMMode.SW, PWMMode.TH], config_class = PWMMode))

        general_items = general_items + [
            MultiSelectMenuItem(self, config, "pwm_brake_mode", [BrakeMode.SIMPLE, BrakeMode.SMART, BrakeMode.LIFT_OFF_DELAY], config_class = BrakeMode),
            AdjustFadeSpeedMenuItem(self),
            ToggleMenuItem(self, config, "primary_button_reverse", config_class = ButtonModeReverse),
            MultiSelectMenuItem(self, config, "secondary_button_mode", [ButtonMode.NONE, ButtonMode.BRAKE, ButtonMode.FLASH, ButtonMode.EMERGENCY_TOGGLE], config_class = ButtonMode),
            SteeringThresholdMenuItem(self),
            SubMenu(self, 
                title = "Sleep mode",
                items = (
                    QuitMenu(self),
                    HybridMenuItem(self, config, "sleep_delay", [0, 5, 10, 30, 60], config_class = SleepDelayConfig, units = 's'),
                    ToggleMenuItem(self, config, "sleep_when_lights_on", config_class = SleepWhenLightsOnMode),
                    AdjustBreatheTimeMenuItem(self),
                    AdjustBreatheGapMenuItem(self),
                    HybridMenuItem(self, config, "breathe_min_brightness", [0, 10, 20, 30, 50], config_class = BreatheMinimumBrightnessConfig, units = '%'),
                )
            ),
            SubMenu(self,
                title = "Emergency flash",
                items = (
                    QuitMenu(self),
                    MultiSelectMenuItem(self, config, "emergency_mode", [EmergencyMode.OFF, EmergencyMode.MODE_2, EmergencyMode.MODE_1_2], config_class = EmergencyMode),
                    AdjustEmergencyFlashPeriodMenuItem(self),
                    MultiSelectMenuItem(self, config, "emergency_flashes_per_side", list(range(1, 7)), config_class = EmergencyFlashCountConfig),
                    ToggleMenuItem(self, config, "emergency_fade", config_class = EmergencyFadeMode),
                )
            ),
            SubMenu(self, 
                title = "Alarms",
                items = (
                    QuitMenu(self),
                    ToggleMenuItem(self, config, "esc_temperature_alarm_enable", config_class = ESCTemperatureAlarmEnable),
                    GenericLevelAdjusterMenuItem(self, config, ESCTemperatureAlarm),
                )
            ),
        ]
        self.menu.add(SubMenu(self, 
            title = "General settings",
            items = general_items
        ))
        for (i, l) in enumerate(self.vehicle.lights):
            repeat_text = "As for output 1" if i > 0 else None
            submenu = SubMenu(self, [
                QuitMenu(self),
            ], light = l, title = "Output %d" % (i + 1), config_path="lights[%d]" % i, repeat_text = repeat_text)

            for state in LightStates:
                submenu.add(AdjustLightLevelMenuItem(self, l, state))
            self.menu.add(submenu)


    def spec(self):
        return self.menu.spec()

    def start(self):
        self.menu_pos = 0
        self.menu_depth = 0 
        for l in self.vehicle.all_lights:
            l.animate(SimpleAnimation.multi_flash(1), menu = True)
        self.menu_stack = [(self.menu, 0)]
        self.clear_all()
        self.last_wrap = time.ticks_ms()

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
                # If we've just wrapped back to the first item, ignore further
                # clicks until a gap of at least 0.75s
                if self.last_wrap is not None and time.ticks_ms() - self.last_wrap < 750:
                    self.last_wrap = time.ticks_ms()
                else:
                    self.menu_pos = (self.menu_pos + 1) % cur_menu.length
                    item = cur_menu.items[self.menu_pos]
                    self.flash_all(self.menu_pos + 1)
                    item.select()
                    if self.menu_pos == 0:
                        self.last_wrap = time.ticks_ms()
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
            s = cur_menu.items[self.menu_pos].spec()
            if s is not None:
                print("LOG %s" % s.get("title"))
            else:
                print("LOG Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))
        elif isinstance(cur_menu, (LevelAdjusterMenuItem, MultiSelectMenuItem, SteeringThresholdMenuItem)):
            if not cur_menu.click(event):
                self.go_up()

        return True

    def level_setting(self, level):
        (cur_menu, n) = self.menu_stack[-1]
        cur_menu.level_setting(level)
