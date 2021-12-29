from button import ButtonEvent
from light import Animation

class MenuItem:

    def __init__(self, menu, light = None):
        self.light = light
        self.menu = menu

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(50)

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


class AdjustLevelMenuItem(MenuItem):

    def __init__(self, menu, light, state):
        super().__init__(menu, light)
        self.state = state
        self.cur_value = getattr(light, state)

    def level_setting(self, level):
        self.light.set_level(level)
        self.cur_value = level

    def click(self, event):
        if event == ButtonEvent.LONG_CLICK:
            setattr(self.light, self.state, self.cur_value)
            return False
        return True

    def select(self):
        self.menu.clear_all()
        if self.light:
            self.light.set_level(getattr(self.light, self.state, 0))

class Menu:

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.menu = SubMenu(self)
        self.menu.add(QuitMenu(self))
        for l in self.vehicle.lights:
            submenu = SubMenu(self, (
                QuitMenu(self),
                AdjustLevelMenuItem(self, l, "on_level"),
                AdjustLevelMenuItem(self, l, "off_level"),
            ), light = l)
            self.menu.add(submenu)

    def start(self):
        self.menu_pos = 0
        self.menu_depth = 0 
        for l in self.vehicle.lights:
            l.animate(Animation.multi_flash(1))
        self.menu_stack = [(self.menu, 0)]
        self.clear_all()

    def adjust_level(self):
        pass

    def flash_all(self, n):
        for l in self.vehicle.lights:
            l.animate(Animation.multi_flash(n))

    def clear_all(self):
        for l in self.vehicle.lights:
            l.set_level(0)

    def go_up(self):
        print("Up")
        (submenu, self.menu_pos) = self.menu_stack.pop()
        if len(self.menu_stack) == 0:
            print("Leaving menu")
            return False
        else:
            self.flash_all(self.menu_pos + 1)
            self.menu_stack[-1][0].items[self.menu_pos].select()
        return True

    def click(self, event):
        (cur_menu, n) = self.menu_stack[-1]
        print("Event: %d" % event)

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
                elif type(item) == AdjustLevelMenuItem:
                    self.menu_stack.append((item, self.menu_pos))
                if type(item) == QuitMenu:
                    if not self.go_up():
                        return False
            print("Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))
        elif (type(cur_menu) == AdjustLevelMenuItem):
            if not cur_menu.click(event):
                self.go_up()
            print("Depth: %d Pos: %d" % (len(self.menu_stack), self.menu_pos))


        return True

    def level_setting(self, level):
        (cur_menu, n) = self.menu_stack[-1]
        if type(cur_menu) == AdjustLevelMenuItem:
            cur_menu.level_setting(level)
