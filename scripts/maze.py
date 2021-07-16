from random import choice
from ..ctrl.color import _WHITETUP
from ..ctrl.npwrap import MyNeoPixel
from ..dca.twod import MyLifelikeNeoPixel, iter4neighboridxs

class MyMazeNeoPixel(MyNeoPixel):

    def __init__(self, cfg, color=None):
        from color import RGB
        super().__init__(cfg)
        self.color = color if color is not None else RGB(255, 0, 0)  # default is red in this case
        #initnp = MyLifelikeNeoPixel(cfg, brule=[2,3], srule=[1,2,3,4])
        initnp = MyLifelikeNeoPixel(cfg, brule=[2,3], srule=[1,2,3,4,5])
        while 1:
            initnp.run() # goes until stable
            if any(initnp.binbuf): break  # if nontrivial maze, continue
        idxs = []
        for i in range(N):
            if initnp.binbuf[i]:
                self[i] = _WHITETUP
                idxs.append(i)
        start_idx = choice(idxs)
        self[start_idx] = self.color
        self.front_idxs = set([start_idx])

    def update(self):
        while len(self.front_idxs) > 0:
            i = choice(self.front_idxs)
            for j in iter4neighboridxs(i):
                if self[j] == _WHITETUP:
                    self[j] = self.color
                    self.front_idxs.add(j)
            self.front_idxs.remove(i)
    
def main(cfg):
    from time import sleep_us
    np = MyMazeNeoPixel(cfg)
    while 1:  # make one solution after another
        np.run()
        sleep_us(np.dt_us*5)  # show solution for a while

def demo(cfg, timeout):
    np = MyMazeNeoPixel(cfg)
    np.run(timeout=timeout)