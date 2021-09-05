from math import sqrt, asin, atan, pi, inf, radians, sin, cos, atan2

A = 6378137
B = 6356752.314245

e2 = 1 - B * B / (A * A)
f = 1 - B / A


def cart2lle(x, y, z):
    r = sqrt(x ** 2 + y ** 2 + z ** 2)
    lon = atan(y / x if x != 0 else inf)
    if x < 0 and y >= 0:
        lon += pi
    if x < 0 and y < 0:
        lon -= pi
    lat = asin(z / r)
    r -= RE
    return lat, lon, r


def cart2geo(x, y, z):
    Rxy = sqrt(x * x + y * y)
    R = sqrt(Rxy * Rxy + z * z)
    m = atan2(z * ((1 - f) + e2 * A / R), Rxy)
    lat = atan2(
        z * (1 - f) + e2 * A * pow(sin(m), 3), (1 - f) * (Rxy - e2 * A * pow(cos(m), 3))
    )
    lon = atan2(y, x)
    h = Rxy * cos(lat) + z * sin(lat) - A * sqrt(1 - e2 * sin(lat) * sin(lat))
    return lat, lon, h


def decdeg2dms(dd):
    mnt, sec = divmod(dd * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return deg, mnt, round(sec, 1)


def gsc2tsc(xyz, xyz_s, **kwargs):
    xs, ys, zs = xyz_s
    x, y, z = xyz
    lat = kwargs["lat"]
    lon = kwargs["lon"]
    _x = -(x - xs) * sin(lon) + (y - ys) * cos(lon)
    _y = -((x - xs) * cos(lon) + (y - ys) * sin(lon)) * sin(lat) + (z - zs) * cos(lat)
    _z = ((x - xs) * cos(lon) + (y - ys) * sin(lon)) * cos(lat) + (z - zs) * sin(lat)
    return _x, _y, _z
