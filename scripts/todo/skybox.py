from micropython import const
from urequests import get as sendget
from framebuf import FrameBuffer, RGB565
from math import cos, sin
from ...util.sinusoid import _TWOPI, gen2ds
from ...util.translate import buf2xy
from ...util.util import sigmoid
import ntptime
from time import time
from ...ctrl.color import RGB, HSV, interphsv, _WHITEHSV

_SKYBLUEHSV = const(HSV(140, 110, 235))
_CLOUDWHITERGB = RGB(37, 150, 190)
_CLOUDWHITERGB.setmaxvalue()
_DEEPSKYBLUERGB = RGB(0, 191, 255)
_DEEPSKYBLUERGB.setcurrent(_CLOUDWHITERGB.current_draw)
_DEEPSKYBLUEHSV = const(_DEEPSKYBLUERGB.to_hsv())
_CLOUDWHITEHSV = const(_CLOUDWHITERGB.to_hsv())

def apiaddr(zip_code, api_key):
    return "api.openweathermap.org/data/2.5/weather?zip={}&appid={}&units=imperial".format(zip_code, api_key)

class Clouds:

    def __init__(self, spaceperiods, spacedirs):
        self.ks = []
        self.ws = []
        for spaceperiod, spacedir in zip(spaceperiods, spacedirs):
            k = _TWOPI / spaceperiod
            self.ks.append((k*cos(spacedir), k*sin(spacedir)))

    def apply_daylight(self, sky_color, cloud_color, daylight):
        this_sky_color = sky_color
        # from near darkness to full brightness
        this_sky_color.scale(0.05 + 0.95 * daylight)
        this_cloud_color = cloud_color
        # clouds are slightly brighter than sky at night because of wash from the light pollution
        this_cloud_color.scale(0.1 + 0.9 * daylight)
        # get cloud edge color: completely cloud colored in night, slightly bluish in day
        this_edge_color = interphsv(this_cloud_color, this_sky_color, 0.2 * daylight)
        # scale cloud edge color: darker at night relative to cloud, lighter in day
        this_edge_color.scale(0.85 + 0.3 * daylight)
        return this_sky_color, this_edge_color, this_cloud_color

    def getraw(self, ws, x, y, t):
        return gen2ds(self.ks, ws, x, y, t)  # always in [0,1]

    def getbuf(self, sky_color, cloud_color, daylight, cloudp, windspeed, winddir, t):
        sky_color, edge_color, cloud_color = self.apply_daylight(sky_color, cloud_color, daylight)
        if cloudp == 0:
            return [sky_color.to_rgb().as_tuple()]*N
        else:
            buf = [edge_color.to_rgb().as_tuple()]*N
            if cloudp == 1:
                # add some small waves so it's not a single color
                cloudp = 0.95
            for i in range(N):
                # interpolate between sky and cloud, 
                # setting gradient cloud -> edge -> sky
                # so that edge color is the result when raw == cloudp
                raw = self.getraw(*buf2xy(i), t)
                if raw < cloudp:
                    buf[i] = interphsv(cloud_color, edge_color, raw / cloudp, return_type="rgb").as_tuple()
        return buf


class MySkyboxNeoPixel(MyNeoPixel):

    def __init__(self, cfg):
        self.addr = apiaddr(cfg["zip_code"], cfg["weather_api_key"])
        self.clouds = Clouds()
        self.rainbuf = bytearray([255]*N)
        self.get_interval = 3 * 60  # time in seconds between gets (api updates every 10, we use largest coprime smaller than half for more up-to-date conditions on average)
        self.time_of_last_get = None

    def getdata(self):
        response = sendget(self.addr)
        data = response.json()
        response.close()
        ntptime.settime(timezone=-8, server="time.nist.gov")
        return {
            "wind" : {
                "speed" : data["wind"]["speed"],
                "dir" : 360 - data["wind"]["deg"]  # direction of travel
            },
            "clouds" : data["clouds"]["all"],
            "rain" : data["rain"]["1h"],
            "time" : {
                "sunrise" : data["sys"]["sunrise"],
                "sunset" : data["sys"]["sunset"]
            }
        }
  
    def update(self):
        pass
        # cloud effect: 
        #   1. make smoothish noise function (maybe just a few sinusoids), 
        #   2. animate it by moving in wind direction, 
        #   3a. interp between sky (0) and cloud edge (1-cloudpctg) with sigmoid,
        #   3b. interp between cloud edge (1-cloudpctg) and cloud center (1) with linear,
        #   3c. ensuring that the gradient of the sigmoid at the boundary is the slope of the linear part
        # rain effect: slight pointwise dimming (sharp attack, slow decay) (maybe instead brightens at night? refraction?)
        # wind effect: slight strokewise brightening  (stretched ellipses moving in front of clouds?)
        # sunlight effect: global brightness varies with estimated sunlight
        # animation parameters should be exponentially-smoothed vs most recent reading to avoid sharp jumps
