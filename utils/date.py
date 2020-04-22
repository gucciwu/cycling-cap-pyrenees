# %%

import datetime
import logging
import time
import pytz

from dateutil import parser

logger = logging.getLogger(__name__)


def now():
    return datetime.datetime.now()


def get_now_str():
    return now().strftime("%Y%m%d%H%M%S")


def get_now_date_str():
    return now().date().strftime("%Y%m%d")


def get_14(dt=None):
    if dt is None:
        dt = now()
    return dt.strftime("%Y%m%d%H%M%S")


def get_8(dt=None):
    if dt is None:
        dt = now()
    return dt.date().strftime("%Y%m%d")


def get_10(dt=None):
    if dt is None:
        dt = now()
    return dt.date().strftime("%Y-%m-%d")


def get_25(dt=None):
    if dt is None:
        dt = now()
    dt = add_timezone(dt, 'PRC')
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def local_to_timestamp(dt):
    """
    convert datetime to timestamp
    """
    dt = parse_datetime(dt)
    ts = time.mktime(dt.timetuple())
    return int(ts)


def timestamp_to_utc_datetime(ts):
    """
    convert timestamp to datetime
    """
    return datetime.datetime.utcfromtimestamp(ts)


def transform_timezone(dt, from_tz_str, to_tz_str):
    """
    convert datetime from from_tz to to_tz
    """
    if from_tz_str == to_tz_str:
        return dt
    tz_from = pytz.timezone(from_tz_str)
    tz_to = pytz.timezone(to_tz_str)
    dt = parse_datetime(dt)
    local_dt = tz_from.localize(dt)
    ret = local_dt.astimezone(tz_to)
    return ret


def add_timezone(dt, tz_str):
    """
    add timezone information in datetime
    @:param dt: UTC datetime
    """
    dt = parse_datetime(dt)
    return dt.astimezone(pytz.timezone(tz_str))


def clean_datetime_str(dt_str):
    if isinstance(dt_str, str):
        ret = dt_str.replace(':', '').replace('-', '').replace(' ', '')
        if len(ret) > 14:
            return ret[:14]
        return ret
    return dt_str


def parse_datetime(dt):
    if isinstance(dt, str):  # datetime string
        dt_str = clean_datetime_str(dt)
        return parser.parse(dt_str)
    if isinstance(dt, int):  # should be timestamp
        return timestamp_to_utc_datetime(dt)
    return dt
