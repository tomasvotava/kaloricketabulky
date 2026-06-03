from datetime import date, datetime
from zoneinfo import ZoneInfo

from kaloricketabulky.sdk._dates import (
    format_path_date,
    format_query_date,
    from_epoch_ms,
    parse_dmy,
)

PRAGUE = ZoneInfo("Europe/Prague")


def test_from_epoch_ms_is_prague_midnight() -> None:
    result = from_epoch_ms(1780351200000)
    assert result == datetime(2026, 6, 2, tzinfo=PRAGUE)
    assert result.tzinfo is not None
    assert result.date() == date(2026, 6, 2)


def test_from_epoch_ms_none() -> None:
    assert from_epoch_ms(None) is None


def test_format_path_date() -> None:
    assert format_path_date(date(2026, 6, 2)) == "02.06.2026"


def test_format_query_date() -> None:
    assert format_query_date(date(2026, 6, 2)) == "2026-06-02"


def test_parse_dmy() -> None:
    assert parse_dmy("02.06.2026") == date(2026, 6, 2)
    assert parse_dmy(None) is None
