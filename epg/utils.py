'''
This file includes utils for grab and generate EPG.
They are referenced in main.py.
Many functions are verbose. They print out the progress.
Maybe I should add a verbose option. Or use logging.
'''

import yaml
import importlib
from epg.model import Channel
from datetime import datetime, date, timedelta
from epg.scraper import tz_shanghai


def load_config(path: str) -> list[Channel]:
    """
    Load channels config from yaml file.

    Args:
        path (str): The path of the yaml file.
    
    Returns:
        list[Channel]: The channels.
    """
    channels = []
    with open(path, 'r') as stream:
        try:
            channels_config = yaml.safe_load(stream)
            for channel_id in channels_config:
                metadata = channels_config[channel_id]
                metadata.update({"last_update": datetime(
                    1970, 1, 1, 0, 0, 0, tzinfo=tz_shanghai)})
                channels.append(
                    Channel(
                        channel_id, metadata, lambda channel, date: scrap_channel(
                            channel, channels_config, date)
                    )
                )
        except yaml.YAMLError as exc:
            print(exc)
    return channels

def scrap_channel(channel: Channel, channels_config, date: date = datetime.today().date()) -> bool:
    """
    Scrap channel with the given date.

    Args:
        channel (Channel): The channel to scrap.
        channels_config (dict): The channels config.
        date (date, optional): The date to scrap. Defaults to datetime.today().date().
    
    Returns:
        bool: True if the channel is updated, False otherwise.
    """
    channel.metadata["last_scraper"] = "FAILED"
    for scraper in channels_config[channel.id]["scraper"]:
        scraper_module = importlib.import_module("epg.scraper" + "." + scraper)
        update = getattr(scraper_module, "update")
        if update(channel, channels_config[channel.id]["scraper"][scraper], date):
            channel.metadata["last_scraper"] = scraper
            channel.metadata["last_update"] = datetime.now().astimezone()
            if channel.metadata.get("plugin") != None:
                plugin_module = importlib.import_module(
                    "epg.plugin" + "." + channel.metadata["plugin"])
                plugin_update = getattr(plugin_module, "update")
                plugin_update(channel, date)
            return True
    return False


def copy_channels(channels: list[Channel], new_channels: list[Channel]) -> tuple[int, set]:
    """
    Copy channels from new_channels to channels.
    
    Args:
        channels (list[Channel]): The channels to copy to.
        new_channels (list[Channel]): The channels to copy from.
    
    Returns:
        tuple[int, set]: The number of reused channels and the dates of the programs.
    """
    num_reuse_channels = 0
    dates = set()
    for channel in channels:
        for new_channel in new_channels:
            if channel.id == new_channel.id:
                # Keep the programs in recap days
                for program in new_channel.programs:
                    recap_days = channel.metadata.get("recap") if channel.metadata.get(
                        "recap") != None else 0
                    preview_days = channel.metadata.get("preview") if channel.metadata.get(
                        "preview") != None else 0
                    if datetime.now().date() + timedelta(preview_days) >= program.start_time.date() >= datetime.now().date() - timedelta(recap_days):
                        dates.add(program.start_time.date())
                        channel.programs.append(program)
                num_reuse_channels += 1
                channel.programs = list(
                    set(channel.programs))  # Remove duplicates
                # print("reuse channel:", channel.id, channel.metadata["name"], xml_channel.metadata["last_update"].astimezone().isoformat(), channel.metadata["refresh"])
                if channel.programs != []:
                    channel.metadata["last_update"] = new_channel.metadata["last_update"]
                else:
                    channel.metadata["last_update"] = datetime(1970, 1, 1, 0, 0, 0, tzinfo=tz_shanghai)
                break
    return (num_reuse_channels, dates)


def update_preview(channel: Channel) -> int:
    """
    Update channel preview.
    
    Args:
        channel (Channel): The channel to update.
    
    Returns:
        int: The number of days previewed."""
    previewed_days = 0
    if channel.metadata.get("preview") == None:
        return previewed_days
    if channel.metadata["preview"] > 0:
        max_date = datetime.now().date() + \
            timedelta(channel.metadata["preview"])
        channel_max_date = datetime.now().date()
        # for program in channel.programs:
        #     if program.start_time.date() > channel_max_date:
        #         channel_max_date = program.start_time.date()
        if channel_max_date < max_date:
            print("preview <- ", end="", flush=True)
        else:
            print("no need to refresh preview", flush=True)
        while channel_max_date < max_date:
            channel_max_date += timedelta(1)
            if channel.update(channel_max_date):
                if channel_max_date < max_date:
                    print(channel_max_date, channel.metadata["last_scraper"], end=", ", flush=True)
                else:
                    print(channel_max_date, channel.metadata["last_scraper"], flush=True)
    return previewed_days


def update_recap(channel: Channel) -> int:
    """
    Update channel recap.
    
    Args:
        channel (Channel): The channel to update.
    
    Returns:
        int: The number of days recaped."""
    recaped_days = 0
    if channel.metadata.get("recap") == None:
        return recaped_days
    if channel.metadata["recap"] > 0:
        min_date = datetime.now().date() - \
            timedelta(channel.metadata["recap"])
        channel_min_date = datetime.now().date()
        for program in channel.programs:
            if program.start_time.date() < channel_min_date:
                channel_min_date = program.start_time.date()
        if channel_min_date > min_date:
            print("recap <- ", end="", flush=True)
        else:
            print("no need to refresh recap", flush=True)
        while channel_min_date > min_date:
            channel_min_date -= timedelta(1)
            if channel.update(channel_min_date):
                recaped_days += 1
                if channel_min_date > min_date:
                    print(channel_min_date, channel.metadata["last_scraper"], end=", ", flush=True)
                else:
                    print(channel_min_date, channel.metadata["last_scraper"], flush=True)
    return recaped_days

def update_channel_full(channel, num_refresh_channels):
    """
    Update channel full.
    
    Args:
        channel (Channel): The channel to update.
        num_refresh_channels (int): Counter of the number of channels that have been refreshed.
    """
    def _update_recap(channel):
        recaped_days = update_recap(channel)
        if recaped_days > 0:
            print("total:", recaped_days, flush=True)
            return True
        return False

    def _update_preview(channel):
        previewed_days = update_preview(channel)
        if previewed_days > 0:
            print("total:", previewed_days, flush=True)
            return True
        return False

    if channel.metadata["refresh"] == "today":
        print(num_refresh_channels + 1, channel.id,
              channel.metadata["name"], "last update:", channel.metadata["last_update"])
        _update_recap(channel)
        _update_preview(channel)
        # Make sure today's programs are the last one to update, so that plugins can influence previews.
        print(channel.metadata["refresh"], "<- now", datetime.now().astimezone().isoformat(), end=" ", flush=True)
        if channel.update():
            print(channel.metadata["last_scraper"], flush=True)
        return True
    if channel.metadata["refresh"] == "once":
        if channel.metadata["last_update"].date() != datetime.now().date():
            print(num_refresh_channels + 1, channel.id,
                  channel.metadata["name"], "last update:", channel.metadata["last_update"])
            _update_recap(channel)
            _update_preview(channel)
            # Make sure today's programs are the last to one update, so that plugins can influence previews.
            print(channel.metadata["refresh"],
                  "<-", datetime.now().isoformat(), end=" ", flush=True)
            channel.update()
            print(channel.metadata["last_scraper"], flush=True)
            return True
    return False