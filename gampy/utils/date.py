from datetime import datetime, timedelta


def doy2date(year, doy, **kwards):
    return datetime(year, 1, 1, 0, 0, 0) + timedelta(days=doy - 1, **kwards)


def date2doy(date):
    return (date - datetime(date.year, 1, 1, 0, 0, 0)).days + 1


def ut(year, doy, min_ut, max_ut, step):
    min_h, min_mnt, min_sec = min_ut
    max_h, max_mnt, max_sec = max_ut
    return [
        doy2date(year, doy, seconds=seconds)
        for seconds in range(
            min_h * 3600 + min_mnt * 60 + min_sec,
            max_h * 3600 + max_mnt * 60 + max_sec,
            step,
        )
    ]
