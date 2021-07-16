from ..dca.twod import MyLifelikeNeoPixel

def main(cfg, color=None, initp=0.5):
    while 1:  # restarts after run ends
        np = MyLifelikeNeoPixel(cfg, color=color, initp=initp)
        np.run()

def demo(cfg, timeout):
    np = MyLifelikeNeoPixel(cfg)
    np.run(timeout=timeout)