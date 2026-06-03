"""Standalone, read-only SDK layer for the kaloricketabulky.cz internal API.

This subpackage is self-contained: it depends only on ``httpx`` and ``pydantic``
and carries no configuration or application concerns, so it can be used on its own
by anyone building their own use case on top of the API.
"""

from kaloricketabulky.sdk.client import KaloricketabulkyClient
from kaloricketabulky.sdk.errors import ApiError, AuthError, KaloricError
from kaloricketabulky.sdk.models.common import Envelope, MeasurementPoint, WeekBar
from kaloricketabulky.sdk.models.diary import (
    Diary,
    DiaryActivity,
    DiaryFoodstuff,
    Meal,
)
from kaloricketabulky.sdk.models.snapshot import Snapshot, SnapshotType
from kaloricketabulky.sdk.models.summary import (
    DiarySummary,
    StatisticsSummary,
    SummaryItem,
)
from kaloricketabulky.sdk.models.tips import Tip

__all__ = [
    "ApiError",
    "AuthError",
    "Diary",
    "DiaryActivity",
    "DiaryFoodstuff",
    "DiarySummary",
    "Envelope",
    "KaloricError",
    "KaloricketabulkyClient",
    "Meal",
    "MeasurementPoint",
    "Snapshot",
    "SnapshotType",
    "StatisticsSummary",
    "SummaryItem",
    "Tip",
    "WeekBar",
]
