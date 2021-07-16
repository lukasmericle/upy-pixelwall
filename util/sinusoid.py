from micropython import const
from math import pi, cos, sin

_TWOPI = const(2 * pi)

def gen2d(k, w, x, y, t):
    return 0.5 * (cos(k[0] * x - w[0] * t) + cos(k[1] * y - w[1] * t))

def gen2ds(ks, ws, x, y, t):
    return sum(gen2d(k, w, x, y, t) for k,w in zip(ks, ws)) / len(ks)