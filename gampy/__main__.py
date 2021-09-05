import os
import sys
import json
import logging
import argparse
import numpy as np
import pandas as pd

from math import degrees
from tempfile import gettempdir

from gampy import __version__
from gampy.gamp import Gamp, GampReader
from gampy.utils.date import ut
from gampy.utils.coord import cart2geo
from gampy.utils.commands import copy, uncompress, convert, mkdir, rmdir

ARG_PARSER = argparse.ArgumentParser(
    description="Tool for calculation of the precise point position (PPP) error using GAMP utility."
)
ARG_PARSER.add_argument(
    "-c", "--config", default="gampy.cfg", help="path to configuration file"
)
ARG_PARSER.add_argument("-v", "--version", action="version", version=__version__)

LOGGING_LEVEL = {
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}
logging.basicConfig(
    filename="gampy.log",
    filemode="w",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
LOGGER = logging.getLogger(__name__)


def prepare_files(src_dir, dst_dir, ftype):
    try:
        if len(os.listdir(src_dir)) == 0:
            if ftype == "obs" or ftype == "nav":
                LOGGER.error(f"{ftype} files in {src_dir} not found")
                sys.exit(1)
            else:
                LOGGER.warning(f"{ftype} files in {src_dir} not found")
        else:
            for fname in os.listdir(src_dir):
                file = copy(os.path.join(src_dir, fname), dst_dir)
                if file.endswith(".Z"):
                    LOGGER.info(f"Gampy uncompress the file {file}")
                    file = uncompress(file)
                if file.endswith("d"):
                    LOGGER.info(f"Gampy convert the file {file}")
                    convert(file)
    except Exception as e:
        LOGGER.error(e)
        sys.exit(1)


def main():
    gamp = Gamp()
    gamp_reader = GampReader()
    args = ARG_PARSER.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)

    obs_dir = config.get("obsDir", "obs")
    nav_dir = config.get("navDir", "nav")
    sp3_dir = config.get("sp3Dir", "sp3")
    clk_dir = config.get("clkDir", "clk")
    out_dir = config.get("outDir", "out")
    nav_sys = config.get("navSys", "gps")
    pos_mode = config.get("posMode", "ppp_kinematic")
    log_level = config.get("logLevel", "INFO")

    logging.getLogger().setLevel(LOGGING_LEVEL[log_level])

    temp_dir = gettempdir()
    process_dir = os.path.join(temp_dir, "gampy")
    gamp_out_dir = os.path.join(process_dir, "out")

    mkdir(process_dir)

    prepare_files(nav_dir, process_dir, "nav")
    prepare_files(sp3_dir, process_dir, "sp3")
    prepare_files(clk_dir, process_dir, "clk")
    prepare_files(obs_dir, process_dir, "obs")

    for fname in os.listdir(process_dir):
        file = os.path.join(process_dir, fname)

        if file.endswith("o"):
            gamp.config.update(obs_file=file, nav_sys=nav_sys, pos_mode=pos_mode)
            LOGGER.info(f"GAMP processes the file {file}")
            gamp.run()
        else:
            LOGGER.info(f"Skip not observation file {file}")

    gamp_out_files = os.listdir(gamp_out_dir)
    site_names = [fname[:4] for fname in gamp_out_files]

    doy = int(gamp_out_files[0][4:7])
    year = 2000 + int(gamp_out_files[0][9:11])

    T = ut(year, doy, (0, 0, 0), (23, 59, 59), 30)
    DZ = pd.DataFrame(index=site_names, columns=T + ["lat", "lon"])
    DXY = pd.DataFrame(index=site_names, columns=T)
    DXYZ = pd.DataFrame(index=site_names, columns=T)

    for fname in gamp_out_files:
        try:
            site_name = fname[:4]
            pos_file = os.path.join(gamp_out_dir, fname)
            LOGGER.info(f"Gampy processes the file {pos_file}")
            timestamps, X, Y, Z, dZ, dXY, dXYZ = gamp_reader.calc_pos_error(pos_file)
            for t, x, y, z, dz, dxy, dxyz in zip(timestamps, X, Y, Z, dZ, dXY, dXYZ):
                if t in T:
                    lat, lon = cart2geo(x, y, z)[:2]
                    DZ.at[site_name, "lat"] = degrees(lat)
                    DZ.at[site_name, "lon"] = degrees(lon)
                    DZ.at[site_name, t] = dz
                    DXY.at[site_name, t] = dxy
                    DXYZ.at[site_name, t] = dxyz
        except Exception as e:
            LOGGER.warning(f"File {pos_file}: {e}")

    out_subdir = os.path.join(out_dir, str(year), "{:03d}".format(doy))
    mkdir(out_subdir)

    for t in T:
        lon = DZ["lon"].values
        lat = DZ["lat"].values
        dZ = DZ[t].values
        dXY = DXY[t].values
        dXYZ = DXYZ[t].values

        out_fname = "{}_{:03d}_{:02d}_{:02d}_{:02d}.txt".format(
            year, doy, t.hour, t.minute, t.second
        )
        out_file = os.path.join(out_subdir, out_fname)

        with open(out_file, "w") as f:
            header = "#site  lat  lon  dZ(m)  dXY(m)  dXYZ(m)\n"
            f.write(header)
            for site_name, lt, ln, dz, dxy, dxyz in zip(
                site_names, lat, lon, dZ, dXY, dXYZ
            ):
                line = (
                    site_name
                    + "{:14.2f}".format(lt)
                    + "{:14.2f}".format(ln)
                    + "{:14.2f}".format(dz)
                    + "{:14.2f}".format(dxy)
                    + "{:14.2f}".format(dxyz)
                    + "\n"
                )
                f.write(line)

    rmdir(process_dir)


if __name__ == "__main__":
    main()
