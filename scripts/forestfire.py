from micropython import const
from math import sqrt
from ..ctrl.color import RGB
from ..ctrl.npwrap import MyNeoPixel
from ..dca.twod import iter4neighbors
from ..util.util import coinflip

_EMPTY = const(RGB(0,0,0))
_TREE = const(RGB(0,255,0))
_FIRE = const(RGB(255,0,0))

def isempty(tup):
    return tup == _EMPTY
def istree(tup):
    return tup == _TREE
def isfire(rgb):
    return tup == _FIRE

def hasburningneighbor(np, i):
    for tup in iter4neighbors(np, i):
        if isfire(tup): return True
    return False

class MyForestFireNeoPixel(MyNeoPixel):

    def __init__(self, cfg, initp=0.5, spawnp=1/sqrt(N), strikep=1/N):
        super().__init__(cfg)
        for i in range(N):
            self[i] = _TREE if coinflip(initp) else _EMPTY
        self.spawnp = spawnp
        self.strikep = strikep

    def update(self):
        idxs = []
        upds = []
        for i in range(N):
            if istree(self[i]):
                if hasburningneighbor(self, i) or coinflip(self.strikep): 
                    idxs.append(i)
                    upds.append(_FIRE)
            elif isempty(self[i]):
                if coinflip(self.spawnp): 
                    idxs.append(i)
                    upds.append(_TREE)
            elif isfire(self[i]):
                idxs.append(i)
                upds.append(_EMPTY)
            else:
                raise RuntimeError("cell in forest fire model has a value other than empty, tree, or fire")
        for i,upd in zip(idxs, upds):
            self[i] = upd

def main(cfg, initp=0.5, spawnp=1/sqrt(N), strikep=1/N):
    np = MyForestFireNeoPixel(cfg, initp=initp, spawnp=spawnp, strikep=strikep)
    np.run()

def demo(cfg, timeout):
    np = MyForestFireNeoPixel(cfg)
    np.run(timeout=timeout)