def main(cfg):
    from scripts import solid, waves, rain, rule030, forestfire
    timeout = 12   # == 60 / 5
    while 1:
        solid.demo(cfg, timeout)
        waves.demo(cfg, timeout)
        rain.demo(cfg, timeout)
        rule030.demo(cfg, timeout)
        forestfire.demo(cfg, timeout)
