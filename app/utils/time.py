import datetime
import pytz


def utc_now():
    return datetime.datetime.now(tz=pytz.utc)
