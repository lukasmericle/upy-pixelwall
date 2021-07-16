# cellular automata
from ..ctrl.npwrap import MyBinaryNeoPixel
from ..util.translate import buf2xy, xy2buf

def iter4neighboridxs(i):
    x0, y0 = buf2xy(i)
    for x,y in [(x0-1,y0), (x0,y0-1), (x0+1,y0), (x0,y0+1)]:
        yield xy2buf(x % WIDTH, y % HEIGHT)

def iter4neighbors(buf, i):
    for j in iter4neighboridxs(i):
        yield buf[j]

def iter8neighboridxs(i):
    x0, y0 = buf2xy(i)
    for y in range(y0-1, y0+2):
        for x in range(x0-1, x0+2):
            if x==x0 and y==y0: continue
            yield xy2buf(x % WIDTH, y % HEIGHT)

def iter8neighbors(buf, i):
    for j in iter8neighboridxs(i):
        yield buf[j]

def count8neighbors(buf, i):
    n = 0
    for v in iter8neighbors(buf, i):
        if v: n += 1
    return n

class MyLifelikeNeoPixel(MyBinaryNeoPixel):

    def __init__(self, cfg, color=None, initp=0.5, brule=[3], srule=[2,3]):
        super().__init__(cfg, color=color)
        from ..util.util import coinflip
        self.binbuf = [coinflip(initp) for _ in range(N)]
        self.brule = brule
        self.srule = srule

    # todo: add deque to track cycles
    def _check_complete(self):
        raise NotImplementedError

    def record(self):
        self.from(self.binbuf)

    def update(self):
        newbuf = [False]*N
        for i in range(N):
            n = count8neighbors(self.binbuf, i)
            if self.binbuf[i] and (n in self.srule): newbuf[i] = True
            elif (not self.binbuf[i]) and (n in self.brule): newbuf[i] = True
            # else: newbuf[i] is already False -- no-op
        self.binbuf = newbuf
        self.record()
