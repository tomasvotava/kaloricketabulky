"""Convert between the API's date encodings and Python date/datetime.

The API encodes instants as epoch milliseconds at Europe/Prague local midnight,
formats path segments as DD.MM.YYYY, and the streak query parameter as YYYY-MM-DD.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

PRAGUE = ZoneInfo("Europe/Prague")


def from_epoch_ms(value: int | float | None) -> datetime | None:
    """Convert epoch milliseconds to a Europe/Prague-aware datetime."""
    if value is None:
        return None
    return datetime.fromtimestamp(value / 1000, tz=PRAGUE)


def format_path_date(value: date) -> str:
    """Format a date as the DD.MM.YYYY used in request paths."""
    return value.strftime("%d.%m.%Y")


def format_query_date(value: date) -> str:
    """Format a date as the YYYY-MM-DD used in the streak query parameter."""
    return value.strftime("%Y-%m-%d")


def parse_dmy(value: str | None) -> date | None:
    """Parse a DD.MM.YYYY string (as returned by the statistics summary)."""
    if value is None:
        return None
    return datetime.strptime(value, "%d.%m.%Y").replace(tzinfo=PRAGUE).date()
