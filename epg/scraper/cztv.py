# {
#     "alertMessage": "数据获取成功",
#     "content": {
#         "list": [
#             {
#                 "station_id": 31,
#                 "station_type": 1,
#                 "station_name": "浙江卫视",
#                 "station_date": "20231006",
#                 "station_icon": "http://oss.cztv.com/ucc/20200123/4aaea824fa3e4f8391a6243509de7011.png",
#                 "list": [
#                     {
#                         "duration": "1513000",
#                         "program_status": 1,
#                         "program_allow": "111",
#                         "program_id": 3246029,
#                         "program_replay": 1,
#                         "program_title": "重播10.5亚运时间",
#                         "play_time": "1696521600000"
#                     },
#                     {
#                         "duration": "388000",
#                         "program_status": 1,
#                         "program_allow": "111",
#                         "program_id": 3246030,
#                         "program_replay": 1,
#                         "program_title": "1005串联10",
#                         "play_time": "1696523113000"
#                     },
#                     {
#                         "duration": "2740000",
#                         "program_status": 1,
#                         "program_allow": "111",
#                         "program_id": 3246031,
#                         "program_replay": 1,
#                         "program_title": "丹青中国心(230430 第1季第2期)01正片上V1",
#                         "play_time": "1696523501000"
#                     }
#                 ]
#             }
#         ]
#     },
#     "message": "success",
#     "state": 0
# }

from epg.model import Channel, Program
from datetime import datetime, date, timezone, timedelta
import requests
import json
from . import headers, tz_shanghai


def update(
    channel: Channel, scraper_id: str | None = None, dt: date = datetime.today().date()
) -> bool:
    channel_id = channel.id if scraper_id == None else scraper_id
    date_str = dt.strftime("%Y%m%d")
    url = f"https://p.cztv.com/api/paas/program/{channel_id}/{date_str}"
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
        programs_data = data["content"]["list"][0]["list"]
    except KeyError:
        return False
    # Purge channel programs on this date
    channel.flush(dt)
    # Update channel programs on this date
    for program in programs_data:
        title = program["program_title"]
        start_time = datetime.fromtimestamp(
            int(program["play_time"]) / 1000, tz=tz_shanghai
        )
        end_time = start_time + timedelta(milliseconds=int(program["duration"]))
        channel.programs.append(
            Program(title, start_time, end_time, channel.id + "@tv.cztv.com")
        )
    channel.metadata.update({"last_update": datetime.now(timezone.utc).astimezone()})
    return True
