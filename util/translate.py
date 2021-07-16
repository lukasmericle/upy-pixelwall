def xy2buf(x, y):
    return x + (y * WIDTH)

def buf2xy(i):
    y = i // WIDTH
    x = i - (y * WIDTH)  # effectively d % WIDTH
    return (x, y)

def buf2d(i):
    y = i // WIDTH
    if y % 2 == 0: return i
    x = i - (y * WIDTH)
    return (WIDTH - x) + (y * WIDTH)

def d2buf(i):
    return buf2d(i)  # merely flips every other row: this is apparently symmetric (idempotent)

def xy2d(x, y):
    return buf2d(xy2buf(x, y))

def d2xy(d):
    return buf2xy(d2buf(d))
