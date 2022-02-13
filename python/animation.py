import config
from math import exp

class Animation:
    pass

class BreatheAnimation(Animation):

    def __init__(self, breathe_time, gap, brightness = 100):
        self.breathe_time = breathe_time
        self.gap = gap
        self.length = breathe_time + gap
        self.brightness = brightness

    def value(self, t, loop = False):
        if loop:
            t = t % self.length

        if t > self.length:
            return None

        gamma = 0.14; # affects the width of peak (more or less darkness)
        beta = 0.5; # shifts the gaussian to be symmetric

        if t > self.breathe_time:
            return 0

        return 10*(exp(-(pow(((t/self.breathe_time)-beta)/gamma,2.0))/2.0))*self.brightness/100
        

class SimpleAnimation(Animation):

    def __init__(self, sequence):
        self.sequence = sequence

    @property
    def length(self):
        return self.sequence[-1][1];

    def value(self, t, loop = False):
        if loop:
            t = t % self.length

        if t > self.length:
            return None

        v = None
        for i, (value, ta) in enumerate(self.sequence):
            if (ta <= t and i < len(self.sequence) - 1 and t < self.sequence[i+1][1]):
                v = value
        return v


    def multi_flash(n, start = 150, on = 150, off = 150, invert = False):
        seq = [(0,0)]
        a = 75 if not invert else 0
        b = 0 if not invert else 75
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
