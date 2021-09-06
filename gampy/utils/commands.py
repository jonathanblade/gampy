import os
import sys
import shutil

RNXCMP_DIR = "./3rdparty/RNXCMP"


def uncompress(src):
    if os.name == "nt":
        gzip = os.path.join(sys._MEIPASS, "gzip.exe")
        cmd = f"{gzip} -fd {src}"
    else:
        cmd = f"gzip -fd {src}"
    os.system(cmd)
    return src[:-2]


def copy(src, dst):
    shutil.copy(src, dst)
    return os.path.join(dst, os.path.basename(src))


def rename(src, dst):
    os.rename(src, dst)
    return dst


def rmdir(src):
    if os.path.exists(src):
        shutil.rmtree(src)


def mkdir(src):
    if not os.path.exists(src):
        os.makedirs(src, exist_ok=True)


def convert(src):
    try:
        rnxcmp_dir = sys._MEIPASS
    except AttributeError:
        rnxcmp_dir = RNXCMP_DIR
    if os.name == "nt":
        crx2rnx = os.path.join(rnxcmp_dir, "crx2rnx.exe")
    else:
        crx2rnx = os.path.join(rnxcmp_dir, "crx2rnx")
    cmd = f"{crx2rnx} -d {src}"
    os.system(cmd)
    return src[:-1] + "o"
