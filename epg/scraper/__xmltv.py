import requests
from lxml import etree
from epg.model import Channel, Program
from datetime import datetime
from io import BytesIO
from . import headers
from epg.scraper import tz_shanghai

def get_channels(xmltv_url: str, dtd: etree.DTD | None = None) -> list[Channel]:
    try:
        xml = requests.get(xmltv_url, headers=headers, timeout=5).content
    except:
        print("Failed to get XMLTV")
        return []
    if dtd != None:
        xml_bytes = BytesIO(xml)
        try:
            root = etree.XML(xml_bytes.read())
        except:
            print("XML is not valid")
            return []
        valid = dtd.validate(root)
        if not valid:
            print(dtd.error_log.filter_from_errors()[0])
            return []
    root = etree.XML(xml)
    try:
        last_update = datetime.strptime(root.get("date"), "%Y%m%d%H%M%S %z")
    except (TypeError, ValueError) as e:
        last_update = datetime(1970, 1, 1, 0, 0, 0, tzinfo=tz_shanghai)
    channels = []
    for xml_channel in root.iter("channel"):
        channel_id = xml_channel.get("id")
        channel_names = [x.text for x in xml_channel.iter("display-name")]
        metadata = {"name": channel_names}
        channels.append(Channel(channel_id, metadata))
    for channel in channels:
        channel.metadata.update({"last_update": last_update})
        xml_programmes = root.xpath(f"//programme[@channel='{channel.id}']")
        for xml_programme in xml_programmes:
            start_time = datetime.strptime(xml_programme.get("start"), "%Y%m%d%H%M%S %z")
            end_time = datetime.strptime(xml_programme.get("stop"), "%Y%m%d%H%M%S %z")
            title = xml_programme.find("title").text
            try:
                sub_title = xml_programme.find("sub-title").text
            except:
                sub_title = ""
            desc = xml_programme.find("desc").text if xml_programme.find("desc") is not None else ''
            channel.programs.append(Program(title, start_time, end_time, channel.id + "@xmltv", desc, sub_title=sub_title))
            channel.programs.sort(key=lambda x: x.start_time)
    return channels