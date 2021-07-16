def read_cfg(filename):
    from ujson import load
    f = open(filename, "r")
    cfg = load(f)
    f.close()
    return cfg

def write_cfg(filename, newdict):
    cfg = read_cfg(filename)
    for key in newdict.keys():
        cfg[key] = newdict[key]
    from ujson import dump
    f = open(filename, "w")
    dump(cfg, f)
    f.close()