# cellular automata
from ..ctrl.npwrap import MyBinaryNeoPixel
from ..util.translate import xy2buf

class My1DCANeoPixel(MyBinaryNeoPixel):

    def __init__(self, cfg, rule, color=None, mode=0, initp=0.5):
        super().__init__(cfg, color=color)
        from ..util.util import coinflip
        self.binbuf = [False]*N
        if mode == 0:
            for i in self.iterrowidx(0): self.binbuf[i] = coinflip(initp)
            self.update = self._update_vertical
        elif mode == 1:
            for i in self.itercolidx(0): self.binbuf[i] = coinflip(initp)
            self.update = self._update_horizontal
        self.rule = rule

    def getnext(self, prev):
        num = 0
        for j,k in zip(prev, [4,2,1]):
            if j: num += k
        return (self.rule >> num) % 2 == 1

    def _update_vertical(self):
        self.scroll_down(wrap=False, wiperow=False)
        prev = [False]*3
        for x,i in enumerate(self.iterrowidx(0)):
            for j,xx in enumerate(range(x-1, x+2)):
                prev[j] = self.binbuf[xy2buf(xx % WIDTH, 1)]
            self.binbuf[i] = self.getnext(prev)

    def _update_horizontal(self):
        self.scroll_left(wrap=False, wipecol=False)
        prev = [False]*3
        for y,i in enumerate(self.itercolidx(0)):
            for j,yy in enumerate(range(y-1, y+2)):
                prev[j] = self.binbuf[xy2buf(1, yy % HEIGHT)]
            self.binbuf[i] = self.getnext(prev)