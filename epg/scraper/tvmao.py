import requests
import time
from datetime import date, datetime, timedelta
from epg.scraper import headers
from epg.model import Channel, Program
from . import tz_shanghai

# Credits to https://github.com/supzhang/epg/blob/master/crawl/spiders/tvmao.py
def update(channel: Channel, scraper_id: str | None = None, dt: date = datetime.today().date()) -> bool:
    """
    Update channel with new data for the given date.

    Args:
        channel (Channel): The channel to update.
        scraper_id (str): The scraper id.
        dt (date): The date to update.
    
    Returns:
        bool: True if success, False if not.
    """
    now_date = datetime.now().date()
    request_date = dt
    delta = request_date - now_date
    now_weekday = now_date.weekday()
    need_weekday = now_weekday + delta.days + 1
    if delta.days < 0:
        if abs(delta.days) > now_weekday:
            return False
    if delta.days > 0:
        if delta.days > 6 - now_weekday:
            return False
    id_split = scraper_id.split('-')
    if len(id_split) == 2:
        id = id_split[1]
    elif len(id_split) == 3:
        id = '-'.join(id_split[1:3])
    else:
        id = scraper_id
    url = f"https://lighttv.tvmao.com/qa/qachannelschedule?epgCode={id}&op=getProgramByChnid&epgName=&isNew=on&day={need_weekday}"
    #time.sleep(1)  # 防止 被BAN
    try:
        res = requests.get(url, headers=headers, timeout=5)
    except:
        return False
    if res.status_code != 200:
        return False
    data = res.json()
    try:
        programs_data = data[2]['pro']
    except:
        return False
    # Purge channel programs on this date
    channel.flush(dt)
    # Update channel programs on this date, if any
    if len(programs_data) == 0:
        return False
    temp_program = None
    for program in programs_data:
        title = program['name']
        starttime_str = program['time']
        starttime = datetime.strptime(starttime_str, '%H:%M').astimezone(
            tz_shanghai).replace(year=dt.year, month=dt.month, day=dt.day)
        if temp_program != None:
            temp_program.end_time = starttime
            channel.programs.append(temp_program)
        temp_program = Program(title, starttime, None, channel.id + "@tvmao.com")
    temp_program.end_time = datetime.strptime('00:00', '%H:%M').astimezone(
        tz_shanghai).replace(year=dt.year, month=dt.month, day=dt.day) + timedelta(days=1)
    channel.programs.append(temp_program)
    return True
