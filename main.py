# on this NodeMCU board there is 4MB of flash memory. 

# general tips:
# * use in-place operations where possible
# * if a package is only needed for a particular action, 
#   import it within a function so it is deallocated upon exit, 
#   as long as that function isn't called often

from micropython import const
from math import sqrt
import demo

HEIGHT = const(12)
WIDTH = const(25)
N = const(HEIGHT*WIDTH)
GOLDEN_RATIO = const(0.5 * (sqrt(5) - 1))

def startup_sequence():
    from ctrl.config import read_cfg
    from ctrl.startup import connect_wlan
    cfg = read_cfg("default_home.json")
    connect_wlan(cfg["ssid_wlan"], cfg["ssid_password"])
    return cfg

cfg = startup_sequence()
demo.main(cfg)