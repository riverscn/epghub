from epg.model import Channel, Program
from datetime import datetime, date, timedelta
import requests
from . import headers, tz_shanghai

API_ENDPOINT = "https://www.discoverychannel.com.tw/ajax/getschedule.php"


def update(
    channel: Channel, scraper_id: str | None = None, dt: date = datetime.today().date()
) -> bool:
    channel_id = channel.id if scraper_id == None else scraper_id
    date_str = dt.strftime("%Y-%m-%d")
    r_data = {"date": date_str, "channel": channel_id}
    try:
        res = requests.post(API_ENDPOINT, data=r_data, headers=headers, timeout=5)
    except:
        print("Fail:", API_ENDPOINT)
        return False
    # handle error
    if res.status_code != 200:
        return False
    programs_data = res.json()
    # Purge channel programs on this date
    channel.flush(dt)
    # Update channel programs on this date, if any
    if len(programs_data) == 0:
        return False
    temp_program = None
    for program in programs_data:
        title = program["title"]
        starttime_str = program["publictime"]
        starttime = datetime.strptime(starttime_str, "%Y-%m-%d %H:%M:%S").astimezone(
            tz_shanghai
        )
        if temp_program != None:
            temp_program.end_time = starttime
            channel.programs.append(temp_program)
        temp_program = Program(
            title, starttime, None, channel.id + "@discoverychannel.com.tw"
        )
    temp_program.end_time = datetime.strptime("00:00:00", "%H:%M:%S").astimezone(
        tz_shanghai
    ).replace(year=dt.year, month=dt.month, day=dt.day) + timedelta(days=1)
    channel.programs.append(temp_program)
    return True
