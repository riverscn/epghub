'''
This folder contains all the scrapers.
Define update(channel: Channel, scraper_id: str | None = None, dt: date) is necessary.
'''

from zoneinfo import ZoneInfo

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                   ' AppleWebKit/537.36 (KHTML, like Gecko)'
                   ' Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60'
}

tz_shanghai = ZoneInfo('Asia/Shanghai')
tz_hong_kong = ZoneInfo('Asia/Hong_Kong')