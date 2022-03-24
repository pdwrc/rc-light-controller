import config
from math import exp

class Animation:

    def start(self, start, loop = False, callback = None):
        self.start_time = start
        self.loop = loop
        self.callback = callback

    def done(self, light, now):
        if self.callback is not None:
            self.callback(light, now)

class BreatheAnimation(Animation):

    def __init__(self, breathe_time, gap, brightness = 100, off_brightness = 0):
        self.breathe_time = breathe_time
        self.gap = gap
        self.length = breathe_time + gap
        self.brightness = brightness
        self.off_brightness = off_brightness

    def value(self, now):
        t = now - self.start_time
        if self.loop:
            t = t % self.length

        if t > self.length:
            return None

        gamma = 0.14; # affects the width of peak (more or less darkness)
        beta = 0.5; # shifts the gaussian to be symmetric

        min_brightness = self.brightness*self.off_brightness/100

        if t > self.breathe_time:
            return min_brightness

        return (exp(-(pow(((t/self.breathe_time)-beta)/gamma,2.0))/2.0))*(self.brightness-min_brightness) + min_brightness
        

class Fade(Animation):

    def __init__(self, from_level, to_level, fade_time = None):
        self.from_level = from_level
        self.to_level = to_level
        if fade_time is None:
            self.fade_time = config.config.fade_time

    def value(self, now):
        t = now - self.start_time
        if t > self.fade_time:
            return None
        return min(100, max(0, self.from_level + int(t * (self.to_level-self.from_level) / self.fade_time)))

class SimpleAnimation(Animation):

    def __init__(self, sequence):
        self.sequence = sequence

    @property
    def length(self):
        return self.sequence[-1][1];

    def value(self, now):
        t = now - self.start_time
        if self.loop:
            t = t % self.length

        if t > self.length:
            return None

        v = self.sequence[0][0]
        for i, (value, ta) in enumerate(self.sequence):
            if (ta <= t and i < len(self.sequence) - 1 and t < self.sequence[i+1][1]):
                v = value
        return v


    def multi_flash(n, start = 150, on = 150, off = 150, invert = False, brightness = 75):
        seq = [(0,0)]
        a = brightness if not invert else 0
        b = 0 if not invert else brightness
        for i in range(n):
            seq.append((a, start + (on+off) * i))
            seq.append((b, start + (on+off) * i + on))
        seq.append((b,n * (on+off) + off))
        return SimpleAnimation(seq)

    def flash():
        return SimpleAnimation(((100, 0), (0, 50), (0, 100)))

    def fade(from_level, to_level, speed = None):
        if speed is None:
            speed = config.config.fade_speed
        step = (to_level - from_level) / 5
        return SimpleAnimation(list((int(from_level + step * x), x * speed) for x in range(5)))

    def join(*args):
        t = 0
        animation = []
        for anim in args:
            for (val, tt) in anim.sequence:
                animation.append((val, tt + t))
            t += anim.length

        return SimpleAnimation(animation)

    def faded_flash(on, off, t, fade_speed = None):
        if fade_speed is None:
            fade_speed = config.config.fade_speed
        flash_length = 5*fade_speed

        return SimpleAnimation.join(
                SimpleAnimation.fade(off, on, fade_speed), 
                SimpleAnimation(((on, 0), (on, t-flash_length))),
                SimpleAnimation.fade(on, off, fade_speed), 
                SimpleAnimation(((off, 0), (off, t-flash_length)))
            )

class EmergencyFlash(Animation):

    def __init__(self, brightness1 = 100, brightness2 = 0):
        self.period = 400
        self.flash_time = 100
        self.brightness1 = brightness1
        self.brightness2 = brightness2

    def value(self, now):

        t = (now - self.start_time) % (self.period * 2)
        brightness = self.brightness1 if t // self.period == 0 else self.brightness2

        fade_time = config.config.fade_time
        if fade_time > 0:
            fade = min(t % self.flash_time, fade_time) / fade_time
        else:
            fade = 1
        on = ((t // self.flash_time) % 2) 
        if on == 1:
            return fade * brightness
        else:
            return (1-fade) * brightness

class FadedFlash(Animation):

    def __init__(self, on = 100, off = 0, period = 1000, fade_time = None):
        self.period = period
        self.on = on
        self.off = off
        if fade_time is None:
            self.fade_time = config.config.fade_time
        else:
            self.fade_time = fade_time

    def value(self, now):

        t = (now - self.start_time) 
        
        if not self.loop and t > self.period:
            return None
        t = t % self.period

        brightness = self.on if t*2 // self.period == 0 else self.off

        fade_time = self.fade_time
        if fade_time > 0:
            fade = min(t % (self.period//2), fade_time) / fade_time
        else:
            fade = 1
        on = (2 * t // self.period) == 1
        if on == 1:
            return self.on + int(fade * (self.off-self.on))
        else:
            return self.off + int(fade * (self.on-self.off))
