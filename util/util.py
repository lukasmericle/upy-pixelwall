from random import random
def coinflip(p):
    return random() < p

from math import exp
def sigmoid(x):
    return 1 / (1 + exp(-x))

def interp(x1, x2, t):
    return (1 - t) * x1 + t * x2