import time

CLICK_LENGTH = 500
MULTI_CLICK_GAP = 500
EXTRA_LONG_CLICK_LENGTH = 3000

class ButtonEvent:
    SHORT_CLICK = 1
    LONG_CLICK = 2
    EXTRA_LONG_CLICK = 3
    PRESS = 4
    RELEASE = 5

class ButtonState:

    def __init__(self, channel, callback, reverse = False):
        self.channel = channel
        self.callback = callback
        self.pressed = None
        self.released = None
        self.extra_long_click_sent = False
        self.reverse = reverse
        self.multi_click = 0

    def update(self, pressed):
        if pressed and self.pressed is None:
            # debounce
            if self.released is None or time.ticks_ms() - self.released > 50:
                self.pressed = time.ticks_ms()
                self.extra_long_click_sent = False
                if self.released is not None and self.pressed - self.released < MULTI_CLICK_GAP:
                    self.multi_click += 1
                else:
                    self.multi_click = 0
                self.callback(ButtonEvent.PRESS)
        elif pressed and time.ticks_ms() - self.pressed > EXTRA_LONG_CLICK_LENGTH and not self.extra_long_click_sent:
            self.extra_long_click_sent = True
            self.callback(ButtonEvent.EXTRA_LONG_CLICK)
        elif not pressed and self.pressed:
            self.released = time.ticks_ms()
            if self.pressed is not None and not self.extra_long_click_sent:
                self.callback(ButtonEvent.RELEASE)
                long_click = self.released - self.pressed > CLICK_LENGTH
                if long_click:
                    self.callback(ButtonEvent.LONG_CLICK)
                else:
                    self.callback(ButtonEvent.SHORT_CLICK)
            self.pressed = None

