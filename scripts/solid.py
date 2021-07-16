from ..ctrl.color import RGB
from ..ctrl.npwrap import MyBinaryNeoPixel

def main(cfg, color=None):
    np = MyBinaryNeoPixel(cfg, color=color)
    np.fill()
    np.write()

def demo(cfg, timeout):
    from time import sleep
    main(cfg, color=RGB(255, 0, 0))
    sleep(timeout/3)
    main(cfg, color=RGB(0, 255, 0))
    sleep(timeout/3)
    main(cfg, color=RGB(0, 0, 255))
    sleep(timeout/3)