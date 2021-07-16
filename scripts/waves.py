from math import pi, cos, sin, trunc
from ..ctrl.color import _RAINBOWCYCLE, RGB, interphsv
from ..ctrl.npwrap import MyChromoNeoPixel

class MyWavesNeoPixel(MyChromoNeoPixel):
    
    def __init__(self, cfg, wavelength=7, wavespeed=1, direction=0.25*pi, colors=None):
        super().__init__(cfg)
        k = 2 * pi / wavelength
        w = k * wavespeed
        cosdir = cos(direction)
        sindir = sin(direction)
        self.k = [k * cosdir, k * sindir]
        self.w = [w * cosdir, w * sindir]
        self.t = 0
        if self.colors is None:
            self.colors = _RAINBOWCYCLE
        else:
            self.colors = [RGB.from(color) for color in colors]

    def getcolor(self, x, y):  # p in [0, len(self.colors)]
        # linear interpolation over the color palette stored in self.colors
        p = 0.25 * (2 + (cos(self.k[0] * x - self.w[0] * self.t) + cos(self.k[1] * y - self.w[1] * self.t)))  # p in [0,1]
        nc = len(self.colors)
        r = nc * p
        c = trunc(r)
        frac = r - c
        return interphsv(self.colors[c], self.colors[(c+1)%nc], frac)

    def update(self):
        self.t += self.dt_us
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.set(x, y, self.getcolor(x, y))

def main(cfg, wavelength=7, wavespeed=1, direction=pi/4, colors=None):
    np = MyWavesNeoPixel(cfg, wavelength=wavelength, wavespeed=wavespeed, direction=direction, colors=colors)
    np.run()

def demo(cfg, timeout):
    np = MyWavesNeoPixel(cfg)
    np.run(timeout=timeout)