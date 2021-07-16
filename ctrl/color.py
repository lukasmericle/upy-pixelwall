from micropython import const
from math import trunc

# conversions follow https://stackoverflow.com/a/22120275

_INV255 = const(1. / 255)

_BLACKTUP = const((0, 0, 0))
_WHITETUP = const((255, 255, 255))

def attenuate_tuple(tup, scale):
    if scale >= 1: return tup
    if scale == 0: return _BLACKTUP
    return tuple(trunc(scale * led) for led in tup)

def tupvalue(rgbtup):
    return sum(rgbtup) * _INV255

class Color:

    def set(self, i, v):
        if isinstance(v, float): v = trunc(v * 255)
        self.data[i] = v

    def as_tuple(self):
        return tuple(self.data)

class RGB(Color):

    def __init__(self, r=0, g=0, b=0):
        self.data = bytearray([r, g, b])

    @property
    def r(self):
        return self.data[0]
    @property
    def g(self):
        return self.data[1]
    @property
    def b(self):
        return self.data[2]

    def setr(self, r):
        self.set(0, r)
    def setg(self, g):
        self.set(1, g)
    def setb(self, b):
        self.set(2, b)

    @classmethod
    def from(cls, other):
        if isinstance(other, RGB): return other
        if isinstance(other, tuple): return cls(*other)
        if other is None: return _WHITERGB
        return other.to_rgb()

    def to_hsv(self):
        this_min = min(self.data)
        this_max = max(self.data)
        delta = this_max - this_min
        if delta == 0: return HSV(0, 0, this_max)
        if self.r == this_max: hue = (43 * (self.g - self.b)) / delta
        elif self.g == this_max: hue = 85 + (43 * (self.b - self.r)) / delta
        elif self.b == this_max: hue = 171 + (43 * (self.r - self.g)) / delta
        if hue < 0: hue += 255
        elif hue > 255: hue -= 255
        return HSV(trunc(hue), (255 * delta) // this_max, this_max)

    @property
    def value(self):
        return max(self.data)

    def setmaxvalue(self):
        self.scale(255 / self.value)
    
    def scale(self, s):
        value = self.value
        if value == 0: return
        s = min(s, 255 / value)
        if s == 1: return
        self.setr(trunc(s * self.r))
        self.setg(trunc(s * self.g))
        self.setb(trunc(s * self.b))

    @property
    def current_draw(self):
        return 0.02 * sum(self.data) * _INV255  # 20mA per LED

    def setcurrent(self, current):
        self.scale(current / self.current_draw)

    def __eq__(self, other):
        if isinstance(other, HSV): return self == other.to_rgb()
        return self.as_tuple() == other.as_tuple()

_BLACKRGB = const(RGB(*_BLACKTUP))
_WHITERGB = const(RGB(*_WHITETUP))

class HSV:
    def __init__(self, h=0, s=0, v=0):
        self.data = bytearray([h, s, v])

    @property
    def h(self):
        return self.data[0]
    @property
    def s(self):
        return self.data[1]
    @property
    def v(self):
        return self.data[2]

    def seth(self, h):
        self.set(0, h)
    def sets(self, s):
        self.set(1, s)
    def setv(self, v):
        self.set(2, v)

    @classmethod
    def from(cls, other):
        if isinstance(other, HSV): return other
        if isinstance(other, tuple): return cls(*other)
        if other is None: return _WHITEHSV
        return other.to_hsv()

    def to_rgb(self):
        region = self.h // 43
        remainder = (self.h - (region * 43)) * 6
        p = trunc((self.v * (255 - self.s)) >> 8)
        q = trunc((self.v * (255 - ((self.s * remainder) >> 8))) >> 8)
        t = trunc((self.v * (255 - ((self.s * (255 - remainder)) >> 8))) >> 8)
        if region == 0:
            return RGB(self.v, t, p)
        if region == 1:
            return RGB(q, self.v, p)
        if region == 2:
            return RGB(p, self.v, t)
        if region == 3:
            return RGB(p, q, self.v)
        if region == 4:
            return RGB(t, p, self.v)
        if region == 5:
            return RGB(self.v, p, q)

    @property
    def value(self):
        return self.v

    def setmaxvalue(self):
        self.scale(255 / self.value)

    def scale(self, s):
        if self.v == 0: return
        s = min(s, 255 / self.v)
        self.setv(trunc(s * self.v))

    def __eq__(self, other):
        if isinstance(other, RGB): return self == other.to_hsv()
        return self.as_tuple() == other.as_tuple()

_BLACKHSV = const(HSV(*_BLACKTUP))  # same tuple, just reuse it
_WHITEHSV = const(HSV(0, 0, 255))

_BNWCYCLE = const([_BLACKHSV, _WHITEHSV])
_RAINBOWCYCLE = const([HSV(trunc(x / 7 * 255), 255, 255) for x in range(7)])

def interphsv(c1, c2, frac, return_type="rgb"):
    # simple linear interpolation
    c1hsv = c1 if isinstance(c1, HSV) else c1.to_hsv()
    c2hsv = c2 if isinstance(c2, HSV) else c2.to_hsv()
    inthsv = HSV(trunc(frac * (c2hsv.h - c1hsv.h) + c1hsv.h),
                 trunc(frac * (c2hsv.s - c1hsv.s) + c1hsv.s),
                 trunc(frac * (c2hsv.v - c1hsv.v) + c1hsv.v))
    retstr = return_type.lower()
    if retstr == "hsv": return inthsv
    elif retstr == "rgb": return inthsv.to_rgb()