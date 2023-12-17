"""
This defines Program and Channel model.
Basic proterties and functions.
"""

from datetime import datetime, date, timedelta
from collections.abc import Callable
from typing import Any
from epg.scraper import tz_shanghai


class Program:
    """
    Program model.

    Attributes:
        title (str): The program title.
        start_time (datetime): The program start time.
        end_time (datetime): The program end time.
        channel (str): The channel id.
        desc (str): The program description.
        episode (str): The program episode.
    """

    def __init__(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        channel_id: str,
        desc: str = "",
        episode: str = "",
        sub_title: str = "",
    ) -> None:
        self.title = title
        self.sub_title = sub_title
        self.start_time = start_time
        self.end_time = end_time
        self.desc = desc
        self.episode = episode
        self.channel = channel_id

    def __eq__(self, other) -> bool:
        if isinstance(other, Program):
            return (
                self.start_time == other.start_time
                and self.end_time == other.end_time
                and self.title == other.title
            )
        return False

    def __hash__(self) -> int:
        return hash((self.start_time, self.end_time, self.title))

    def __str__(self) -> str:
        return (
            f"Program({self.channel}, {self.title}, {self.start_time}, {self.end_time})"
        )


class Channel:
    """
    Channel model.

    Attributes:
        id (str): The channel id.
        metadata (dict): The channel metadata.
        programs (list[Program]): The programs of the channel.

    Methods:
        update(date: date = datetime.today().date()) -> bool: Update channel with new data for the given date.
        now_playing(now: datetime = datetime.now()) -> Program | None: Get the program that is currently playing.
        next_program(now: datetime = datetime.now()) -> Program | None: Get the next program.
    """

    def __init__(
        self,
        id: str,
        metadata: dict = {},
        update_callable: Callable[[Any, date], bool] | None = None,
    ) -> None:
        self.__id = id
        self.metadata = metadata
        self.metadata.update(
            {"last_update": datetime(1970, 1, 1, 0, 0, 0, tzinfo=tz_shanghai)}
        )
        self.__update_callable = update_callable
        self.programs = []

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.__id == other
        if isinstance(other, Channel):
            return self.__id == other.__id
        return False

    def __str__(self) -> str:
        return f'Channel(id={self.__id}, name={self.metadata["name"]}, {len(self.programs)} programs)'

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        raise AttributeError("Cannot set attribute 'id'")

    def update(self, date: date = datetime.today().date()) -> bool | tuple:
        """
        Update channel with new data for the given date.

        Args:
            date (date): The date for which to update the model. Defaults to today's date.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if self.__update_callable is not None:
            update_result = self.__update_callable(self, date)
            return update_result
        return False

    def now_playing(self, now: datetime = datetime.now()) -> Program | None:
        """
        Get the program that is currently playing.

        Args:
            now (datetime): The time to check. Defaults to current time.

        Returns:
            Program: The program that is currently playing, or None if no program is playing.
        """
        for program in self.programs:
            if (
                program.start_time.astimezone()
                <= now.astimezone()
                <= program.end_time.astimezone()
            ):
                return program
        return None

    def next_program(self, now: datetime = datetime.now()) -> Program | None:
        """
        Get the next program.

        Args:
            now (datetime): The time to check. Defaults to current time.

        Returns:
            Program: The next program, or None if there is no next program.
        """
        self.programs.sort(key=lambda x: x.start_time)
        for program in self.programs:
            if program.start_time.astimezone() > now.astimezone():
                return program
        return None

    def flush(self, date) -> None:
        """
        Flush all programs of date
        """
        self.programs = [
            program for program in self.programs if program.start_time.date() != date
        ]
        return None
