"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月29日
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name

DB_TZ = ZoneInfo(get_localzone_name())


def convert_tz(dt: datetime) -> datetime:
    """
    Convert timezone of datetime object to DB_TZ.
    """
    dt: datetime = dt.astimezone(DB_TZ)
    print(dt)
    return dt.replace(tzinfo=None)


t = convert_tz(datetime.utcnow())
print(t)
