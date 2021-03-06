import time
from channel import ChannelState

CLICK_LENGTH = 500
MULTI_CLICK_GAP = 500
EXTRA_LONG_CLICK_LENGTH = 1500

class ButtonEvent:
    SHORT_CLICK = 1
    LONG_CLICK = 2
    EXTRA_LONG_CLICK = 3
    EXTRA_LONG_HOLD = 4
    PRESS = 5
    RELEASE = 6


class Button:
    threshold = 20

    def __init__(self,  callback):
        self.callback = callback
        self.pressed = None
        self.released = None
        self.extra_long_click_sent = 0
        self.multi_click = 0

    @property
    def is_pressed(self):
        return self.pressed is not None

    def update(self, state, position = None):
        pressed = (state == ChannelState.FORWARD)
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
        elif pressed and ((time.ticks_ms() - self.pressed) // EXTRA_LONG_CLICK_LENGTH) > self.extra_long_click_sent:
            self.extra_long_click_sent += 1
            self.callback(ButtonEvent.EXTRA_LONG_HOLD, count = self.extra_long_click_sent)
        elif not pressed and self.pressed:
            self.released = time.ticks_ms()
            if self.pressed is not None:
                self.callback(ButtonEvent.RELEASE)
                if self.extra_long_click_sent > 0:
                    self.callback(ButtonEvent.EXTRA_LONG_CLICK, count = self.extra_long_click_sent)
                    self.extra_long_click_sent = 0
                else:
                    long_click = self.released - self.pressed > CLICK_LENGTH
                    if long_click:
                        self.callback(ButtonEvent.LONG_CLICK)
                    else:
                        self.callback(ButtonEvent.SHORT_CLICK)
            self.pressed = None

