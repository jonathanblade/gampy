import os
import sys
import numpy as np
import pandas as pd

from gampy.utils.date import doy2date
from gampy.utils.coord import cart2geo, gsc2tsc

i32 = np.int32
f64 = np.float64

GAMP_DIR = "./3rdparty/GAMP"
GAMP_NAV_SYS = {
    "gps": "1",
    "glo": "4",
    "gps+glo": "5",
    "gal": "8",
    "qzs": "16",
    "bsd": "32",
}
GAMP_POS_MODE = {
    "spp": "0",
    "ppp_kinematic": "6",
    "ppp_static": "7",
}
GAMP_OUT_DFORM = {
    "year": (0, i32),
    "month": (1, i32),
    "day": (2, i32),
    "hour": (3, i32),
    "minute": (4, i32),
    "second": (5, i32),
    "x": (8, f64),
    "y": (9, f64),
    "z": (10, f64),
}


class GampConfig:
    def __init__(self, path):
        self.path = path

    def update(self, obs_file, pos_mode, nav_sys):
        with open(self.path, "r") as config:
            lines = config.readlines()
            lines[1] = lines[1][:22] + obs_file + "\n"
            lines[5] = lines[5][:22] + GAMP_POS_MODE[pos_mode] + "\n"
            lines[7] = lines[7][:22] + GAMP_NAV_SYS[nav_sys] + "\n"

        with open(self.path, "w") as config:
            for line in lines:
                config.write(line)


class Gamp:
    def __init__(self):
        try:
            self.gamp_dir = sys._MEIPASS
        except AttributeError:
            self.gamp_dir = GAMP_DIR
        self.program_path = os.path.join(self.gamp_dir, "gamp")
        self.config = GampConfig(os.path.join(self.gamp_dir, "gamp.cfg"))

    def run(self):
        cmd = f"{self.program_path} {self.config.path}"
        os.system(cmd)


class GampReader:
    def __init__(self):
        pass

    def read(self, pos_file, cols):
        dframe = pd.read_csv(
            pos_file,
            sep="\s+",
            header=None,
            names=cols,
            usecols=[GAMP_OUT_DFORM[col][0] for col in cols],
            dtype={col: GAMP_OUT_DFORM[col][1] for col in cols},
            na_values=["1.#QNB", "-1.#IND"],
        )
        dframe = dframe.dropna()
        return dframe

    def calc_pos_error(self, pos_file):
        dframe1 = self.read(pos_file, ["hour", "minute", "second", "x", "y", "z"])
        dframe2 = dframe1[dframe1.hour >= dframe1.hour[0] + 2]

        pos_fname = os.path.basename(pos_file)
        doy = int(pos_fname[4:7])
        year = 2000 + int(pos_fname[9:11])

        s = dframe1.second.values
        s[s == 29] = 30
        s[s == 59] = 60
        seconds = dframe1.hour.values * 3600 + dframe1.minute.values * 60 + s
        timestamps = [doy2date(year, doy, seconds=int(s)) for s in seconds]

        X = dframe1.x.values
        Y = dframe1.y.values
        Z = dframe1.z.values

        TX = X.copy()
        TY = Y.copy()
        TZ = Z.copy()

        x0 = np.median(dframe2.x.values)
        y0 = np.median(dframe2.y.values)
        z0 = np.median(dframe2.z.values)

        lat0, lon0 = cart2geo(x0, y0, z0)[:2]

        i = 0
        for x, y, z in zip(X, Y, Z):
            tx, ty, tz = gsc2tsc((x, y, z), (x0, y0, z0), **{"lat": lat0, "lon": lon0})
            TX[i] = tx
            TY[i] = ty
            TZ[i] = tz
            i += 1

        dZ = np.abs(TZ)
        dXY = np.sqrt(TX ** 2 + TY ** 2)
        dXYZ = np.sqrt(TX ** 2 + TY ** 2 + TZ ** 2)

        return timestamps, X, Y, Z, dZ, dXY, dXYZ
