"""
Many helpers to support the seemingly simple calendar commands

"Why does everything take a date object?"
It's important each time calendar commands are used, a "fresh" dt.date.today() is passed
Without a fresh object, the bot is stuck at whatever day it was last started
"""

import calendar
import datetime as dt
from dataclasses import dataclass
from random import choice
from typing import Literal

from text_processing import make_possessive


def get_thanksgiving_date(year) -> dt.date | None:
    """Determine a year's Thanksgiving date by getting the fourth Thursday of November"""
    november_month_num = 11
    three_weeks_in_days = 21

    # Get the calendar for the specified month
    november = calendar.monthcalendar(year, november_month_num)

    # Iterate over the weeks in the month
    for week in november:
        # Find first week that has a Thursday
        if week[calendar.THURSDAY]:
            # Calculate the date of the fourth Thursday,
            # by adding 3-weeks worth of days to the first Thursday
            thanksgiving_day = week[calendar.THURSDAY] + three_weeks_in_days
            return dt.date(year, november_month_num, thanksgiving_day)
    return None


@dataclass
class SpecialEvent:
    today: dt.date
    name: str
    date: dt.date
    event_type: Literal["birthday", "holiday"]

    def is_today(self):
        return self.today == self.date

    def is_tomorrow(self):
        return self.date == self.today + dt.timedelta(days=1)

    @property
    def days_until(self):
        return (self.date - self.today).days

    def __str__(self) -> str:
        return self.name

    def __eq__(self, __value: object) -> bool:
        return self.date == __value


def random_birthday_emoji() -> str:
    return choice(["🧁", "🎂", "🍰", "🎉", "🥳", "🎁"])


def birthday_dict(today: dt.date) -> dict[str, dt.date]:
    """Return dict of goon birthdays"""
    # Get year
    current_year = today.year

    # Goon birthdays
    BIRTHDAYS = {
        "Marcos": dt.date(current_year, 2, 3),
        "Hudson": dt.date(current_year, 2, 14),
        "Chris": dt.date(current_year, 4, 21),
        "Alex": dt.date(current_year, 4, 15),
        "Vynle": dt.date(current_year, 5, 9),
        "Justin": dt.date(current_year, 6, 12),
        "Josh": dt.date(current_year, 6, 27),
        "Matt": dt.date(current_year, 9, 24),
        "Hobo": dt.date(current_year, 9, 11),
        "Conrad": dt.date(current_year, 10, 2),
    }

    # Finish birthday title and add emoji
    BIRTHDAYS = {
        f"{make_possessive(goon_name)} birthday {random_birthday_emoji()}": date
        for goon_name, date in BIRTHDAYS.items()
    }

    return BIRTHDAYS


def holiday_dict(today: dt.date) -> dict[str, dt.date]:
    """Return dict of special holidays"""
    # Get year
    current_year = today.year

    HOLIDAYS = {
        "Valentine's Day 💕": dt.date(current_year, 2, 14),
        "Freedom Day 🎇": dt.date(current_year, 7, 4),
        "Halloween 🎃": dt.date(current_year, 10, 31),
        "Thanksgiving 🦃": get_thanksgiving_date(current_year),
        "Christmas 🎄": dt.date(current_year, 12, 25),
        "New Year's Eve 🥳": dt.date(current_year, 12, 31),
    }

    return HOLIDAYS


def get_special_events(today: dt.date, remaining_only: bool) -> list[SpecialEvent]:
    """
    Return list of special events

    Parameters
        remaining_only (bool): Return only the events have yet to occur (or are occuring today)
    """
    # Create lists for holidays and birthdays
    birthday_events = [
        SpecialEvent(today, event_name, event_date, "birthday")
        for event_name, event_date in birthday_dict(today).items()
    ]

    holiday_events = [
        SpecialEvent(today, event_name, event_date, "holiday")
        for event_name, event_date in holiday_dict(today).items()
    ]

    # Combine event types
    events = birthday_events + holiday_events

    # Sort by date
    events = sorted(events, key=lambda e: e.date)

    if remaining_only:
        return [e for e in events if e.days_until > -1]
    return events


# Birthday graveyard 💔
# "Daniel": dt.date(current_year, 4, 3),
# "Lex": dt.date(current_year, 5, 20),
