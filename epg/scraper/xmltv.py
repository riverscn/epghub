import __xmltv
from epg.model import Channel, Program
from datetime import datetime, date, timezone


def update(
    channel: Channel, scraper_params: str, dt: date = datetime.today().date()
) -> bool:
    if scraper_params.find("@http") == -1:
        scraper_url = scraper_params
    else:
        scraper_id = scraper_params.split("@http", 1)[0]
        scraper_url = "http" + scraper_params.split("@http", 1)[1]
    channel_id = channel.id if scraper_id == None else scraper_id
    scraper_channels = __xmltv.get_channels(scraper_url)
    for scraper_channel in scraper_channels:
        if scraper_channel.id == channel_id:
            for program in scraper_channel.programs:
                start_time = program.start_time
                if start_time.date() != dt:
                    continue
                end_time = program.end_time
                title = program.title
                # Purge channel programs on this date
                channel.flush(dt)
                # Update channel programs on this date
                channel.programs.append(
                    Program(title, start_time, end_time, channel.id)
                )
        channel.metadata.update(
            {"last_update": datetime.now(timezone.utc).astimezone()}
        )
        return True
    return False
