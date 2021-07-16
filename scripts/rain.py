from ..ctrl.color import attenuate_tuple, tupvalue
from ..ctrl.npwrap import MyMonoNeoPixel
from ..util.util import coinflip

class MyRainNeoPixel(MyMonoNeoPixel):

    def __init__(self, cfg, color=None, mode=0, initp=0.5, decay_rate=GOLDEN_RATIO, eagerness=0.01):
        super().__init__(cfg, color=color)
        if mode == 0:
            for i in self.iterrowidx(0): self[i] = coinflip(initp)
            self.update = self._update_vertical
        elif mode == 1:
            for i in self.itercolidx(0): self[i] = coinflip(initp)
            self.update = self._update_horizontal
        else:
            raise RuntimeError("Mode not recognized")
        self.mode = mode
        self.p = initp
        self.decay_rate = decay_rate
        self.eagerness = eagerness

    def _update_vertical(self):
        self.scroll_down(wrap=False, wiperow=False)
        for i in self.iterrowidx(0):
            if (tupvalue(self[i]) < self.eagerness) and coinflip(self.p):
                self[i] = self.color  # start new drop
            else:
                self[i] = attenuate_tuple(self[i+WIDTH], self.decay_rate)  # fade drop tail

    def _update_horizontal(self):
        self.scroll_left(wrap=False, wipecol=False)
        for i in self.itercolidx(0):
            if (tupvalue(self[i]) < self.eagerness) and coinflip(self.p):
                self[i] = self.color
            else:
                self[i] = attenuate_tuple(self[i+1], self.decay_rate)


def main(cfg, color=None, mode=0, initp=0.5, decay_rate=GOLDEN_RATIO, eagerness=0.01):
    np = MyRainNeoPixel(cfg, color=color, mode=mode, initp=initp, decay_rate=decay_rate, eagerness=eagerness)
    np.run()

def demo(cfg, timeout):
    np = MyRainNeoPixel(cfg)
    np.run(timeout=timeout)
