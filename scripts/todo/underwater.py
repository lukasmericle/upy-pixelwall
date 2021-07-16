# make it look like you're underwater
import math
from random import random
from micropython import const
from ulab import numpy as np

_RANDN_CONST = const(4 * math.exp(-0.5) / math.sqrt(2.0))

def randn(mu=0, sigma=1, size=1):
    a = np.empty(size)
    if size == 1:
        for i in range(size):
            while True:
                u1 = random()
                u2 = 1.0 - random()
                z = _RANDN_CONST * (u1 - 0.5) / u2
                zz = z * z / 4.0
                if zz <= -math.log(u2):
                    break
            a[i] = z
    if size == 1: return mu + z[0] * sigma
    return mu + z * sigma

def ceilpow2(x):
    return math.trunc(2**math.ceil(math.log2(x)+1e-3))

def init():
    lxs = []
    lzs = []

def _A(L, l):
    return (4 * np.exp(2 * l / L)) / (np.sqrt(np.pi) * L**2 * (2 * l + L))

def phillips_spectrum(k, V, g, l=1):
    L = V**2 / g
    kgt0 = k > 0
    a = np.zeros(len(k))
    a[kgt0] = np.exp(-1/(k[kgt0]*L)**2 - (k[kgt0]*l)**2)
    a[kgt0] /= k[kgt0]**4
    a[kgt0] *= _A(L, l)
    return a

def genwavenums(M):
    k = np.array(range(-M/2, M/2+1))
    k *= 2 * math.pi / M
    return k

def omega(k, g, h):
    return math.sqrt(g * k * math.tanh(k * h))

def h0bar(Lx, Lz, l=1):
    Mp = max(HEIGHT, WIDTH)
    M = ceilpow2(Mp)
    kx = genwavenums(M)
    kz = genwavenums(M)
    realdraws = randn(size=M)
    imagdraws = randn(size=M)


def main(np, cfg, rate=1):
    # simulate trochoidal waves (with reasonable spectrum of wavelengths, etc.)
    # compute normal of surface
    # estimate refraction of light through surface
    # color pixels according to amount of light reaching them
    pass