from ..dca.oned import My1DCANeoPixel

def main(cfg, color=None, mode=0, initp=0.5):
    np = My1DCANeoPixel(cfg, color=color, mode=mode, initp=initp, rule=184)
    np.run()

def demo(cfg, timeout):
    np = My1DCANeoPixel(cfg, rule=184)
    np.run(timeout=timeout)