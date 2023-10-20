# Example:
# {
#     "channel_name": "CCTV1",
#     "date": "2023-10-10",
#     "epg_data": [
#         {
#             "start": "00:00",
#             "end": "00:59",
#             "title": "精彩节目-暂未提供节目预告信息",
#             "desc": ""
#         },
#         {
#             "start": "01:00",
#             "end": "01:59",
#             "title": "精彩节目-暂未提供节目预告信息",
#             "desc": ""
#         }
#     ]
# }

from epg.model import Channel
import json
import os
import shutil

def write(dir: str, channels: list[Channel]) -> bool:
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        shutil.rmtree(dir)
        os.makedirs(dir)
    for channel in channels:
        channel_epg = {}
        for program in channel.programs:
            try:
                channel_epg[program.start_time.strftime(
                    "%Y-%m-%d")]["channel_name"]
            except KeyError:
                channel_epg[program.start_time.strftime(
                    "%Y-%m-%d")] = {}
            channel_epg[program.start_time.strftime(
                "%Y-%m-%d")]["channel_name"] = channel.metadata["name"][0]
            channel_epg[program.start_time.strftime(
                "%Y-%m-%d")]["date"] = program.start_time.strftime("%Y-%m-%d")
            try:
                channel_epg[program.start_time.strftime(
                    "%Y-%m-%d")]["epg_data"]
            except KeyError:
                channel_epg[program.start_time.strftime(
                    "%Y-%m-%d")]["epg_data"] = []
            channel_epg[program.start_time.strftime("%Y-%m-%d")]["epg_data"].append({
                "start": program.start_time.astimezone().strftime("%H:%M"), # astimezone() is necessary
                "end": program.end_time.astimezone().strftime("%H:%M"), # astimezone() is necessary
                "title": program.title,
                "desc": program.desc
            })
        for date in channel_epg:
            json_dir = os.path.join(dir, channel_epg[date]["channel_name"])
            if not os.path.exists(json_dir):
                os.makedirs(json_dir)
            json_path = os.path.join(
                json_dir, channel_epg[date]["date"] + ".json")
            with open(json_path, 'w') as f:
                json.dump(channel_epg[date], f, ensure_ascii=False, indent=4)
    return True
