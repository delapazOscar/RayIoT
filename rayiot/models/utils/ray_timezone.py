import pytz
from datetime import datetime

def convert_utc_in_tz(datetime, tz):
    if not tz:
        tz = 'America/Mexico_City'

    timezone = pytz.timezone(tz)
    try:
        current_time = pytz.utc.localize(datetime)
    except:
        current_time = datetime
    local_time = current_time.astimezone(timezone)
    return local_time, current_time