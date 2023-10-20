from epg.model import Channel, Program
from datetime import datetime, date, timezone
import requests
import json
from . import headers, tz_shanghai


def update(channel: Channel, scraper_id: str | None = None, dt: date = datetime.today().date()) -> bool:
    channel_id = channel.id if scraper_id == None else scraper_id
    date_str = dt.strftime('%Y%m%d')
    url = f'http://api.cntv.cn/epg/getEpgInfoByChannelNew?c={channel_id}&serviceId=tvcctv&d={date_str}&t=json'
    try:
        res = requests.get(url, headers=headers, timeout=5)
    except:
        print("Fail:", url)
        return False
    # handle error
    if res.status_code != 200:
        return False
    data = json.loads(res.text)
    try:
        programs_data = data['data'][channel_id]['list']
    except KeyError:
        return False
    # Purge channel programs on this date
    channel.flush(dt)
    # Update channel programs on this date
    for program in programs_data:
        title = program['title']
        start_time = datetime.fromtimestamp(
            program['startTime'], tz=tz_shanghai)
        end_time = datetime.fromtimestamp(
            program['endTime'], tz=tz_shanghai)
        channel.programs.append(Program(title, start_time, end_time, channel.id  + "@tv.cctv.com"))
    channel.metadata.update({'last_update': datetime.now(
        timezone.utc).astimezone()})
    return True
