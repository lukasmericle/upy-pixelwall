from neopixel import NeoPixel
from time import ticks_us, sleep_us, ticks_add, ticks_diff
from color import attenuate_tuple, RGB, HSV, _INV255, _BLACKTUP, _BLACKRGB
from math import trunc
from ..util import translate

class MyNeoPixel(NeoPixel):

    def __init__(self, cfg):
        from machine import Pin
        super().__init__(Pin("GPIO13", mode=Pin.OUT), N, timing=1)
        self.brightness = cfg["brightness"] / 100
        self.max_current = cfg["maxCurrent"]
        self.dt_us = trunc(1000000 / cfg["frameRate"])

    def __getitem__(self, i):
        # the actual data line zigzags, whereas the typical accessing scheme assumes C-style ordering of 2D array
        return super().__getitem__(translate.buf2d(i))

    def __setitem__(self, i, c):
        if isinstance(c, tuple):
            self[i] = c
        self[i] = RGB.from(c).as_tuple()

    def current_draw(self):
        this_current = 0
        for tup in self:
            this_current += sum(tup)
        this_current *= 0.02 * _INV255  # 20mA per LED
        return this_current

    def _dim(self, frac=1):
        if frac >= 1: return
        for i in range(N):
            self[i] = attenuate_tuple(self[i], frac)

    def _apply_brightness(self):
        self._dim(self.brightness)

    def _safe_max_current(self):
        return self.max_current > 0.06 * N  # 60mA per pixel

    def _apply_max_current(self):
        if self._safe_max_current(): return
        this_current = self.current_draw()
        if this_current > self.max_current:
            self._dim(self.max_current / this_current)

    def _apply_constraints(self):
        self._apply_brightness()
        self._apply_max_current()

    def _iterrowidx(self, y):
        return range(WIDTH*y, WIDTH*(y+1))

    def _itercolidx(self, x):
        return range(x, N, WIDTH)

    def wipe(self):
        super().fill(_BLACKTUP)

    def set(self, x, y, value):
        self[translate.xy2buf(x, y)] = value

    def get(self, x, y):
        return self[translate.xy2buf(x, y)]

    def scroll_down(self, wrap=True, wiperow=True):
        if wrap:
            rowbuf = [self[i] for i in self._iterrowidx(HEIGHT-1)]
        for y in reversed(range(1, HEIGHT)):
            for i in self._iterrowidx(y):
                self[i] = self[i-WIDTH]
        if wrap:
            for x,i in enumerate(self._iterrowidx(0)):
                self[i] = rowbuf[x]
        elif wiperow:  # wiperow ignored if wrap=True
            for i in self._iterrowidx(0):
                self[i] = _BLACKTUP

    def scroll_left(self, wrap=True, wipecol=True):
        if wrap:
            colbuf = [self[i] for i in self._itercolidx(WIDTH-1)]
        for x in reversed(range(1, WIDTH)):  # back to front, so as to perform changes in-place
            for i in self._itercolidx(x):
                self[i] = self[i-1]
        if wrap:
             for y,i in enumerate(self._itercolidx(0)):
                self[i] = colbuf[y]
        elif wipecol:  # wiperow ignored if wrap=True
            for i in self._itercolidx(0):
                self[i] = _BLACKTUP

    def update(self):
        raise NotImplementedError

    def write(self):
        self._apply_max_current()
        super().write()

    def step(self):
        self.update()
        self.write()

    def _check_complete(self):
        return False
    
    def run(self, timeout=None):
        t00 = ticks_us()
        if timeout is not None:
            timeout *= 1000000
            timeout = int(timeout)
        self.write()
        sleep_us(self.dt_us)
        while not self._check_complete():
            t0 = ticks_us()
            t1 = ticks_add(t0, self.dt_us)
            self.step()
            # todo: choose between polling and sleeping. polling is probably faster to react, but sleeping is much lighter on the processor
            while ticks_diff(ticks_us(), t0) < self.dt_us: pass
            # t = ticks_us()
            # if ticks_diff(t, t0) < self.dt_us:
            #     sleep_us(ticks_diff(t1, t))  # wait the rest of the time
            if (timeout is not None) and (ticks_diff(t1, t00) >= timeout):
                break


class MyMonoNeoPixel(MyNeoPixel):

    def __init__(self, cfg, color=None):
        super().__init__(cfg)
        # it is generally recommended to set the color such that at least one channel is max'd
        # note: stored color may be different from given color depending on brightness
        self.color = RGB.from(color)
        self._apply_brightness()
        if self.color == _BLACKRGB:
            raise RuntimeWarning("Color chosen is black, no activity will be apparent in the LEDs")

    def fade(self, value):
        for i in range(N):
            self[i] = attenuate_tuple(self[i], value)

    def from(self, monobuf):
        tup = self.color.as_tuple()
        for i in range(N):
            self[i] = attenuate_tuple(tup, monobuf[i] * _INV255)

    def _apply_brightness(self):
        self.color.scale(self.brightness)

    def _safe_max_current(self):
        return self.max_current > self.color.current_draw * N

    def fill(self, frac=1):
        super().fill(attenuate_tuple(self.color.as_tuple(), frac))


class MyBinaryNeoPixel(MyMonoNeoPixel):

    def __init__(self, cfg, color=None):
        super().__init__(cfg, color=color)
        self._count = 0

    def wipe(self):
        super().wipe()
        self._count = 0

    def fill(self):
        super().fill()
        self._count = N

    def current_draw(self):
        return self._count * self.color.current_draw

    def __setitem__(self, i, truthy):
        # sets to color for any variable which evaluates to True
        if truthy:
            if not self.ison(i): self._count += 1
            self[i] = self.color
        else:
            if self.ison(i): self._count -= 1
            self[i] = _BLACKTUP
    
    def from(self, binbuf):
        for i in range(N):
            self[i] = binbuf[i]
    
    def ison(self, i):
        return self[i] != _BLACKTUP

    def count(self):
        # n = 0
        # for i in range(N):
        #     if self.ison(i): n += 1
        # return n
        return len(filter(self.ison, range(N)))

class MyChromoNeoPixel(MyNeoPixel):

    def rgbfrom(self, rgbbuf):
        for i in range(N):
            self[i] = rgbbuf[i]
        self._apply_brightness()

    def hsvfrom(self, hsvbuf):
        for i in range(N):
            self[i] = HSV(*hsvbuf[i]).to_rgb()
        self._apply_brightness()
