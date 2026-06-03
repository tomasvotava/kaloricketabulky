"""Shared base model, coercion types, and recurring value objects."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from kaloricketabulky.sdk._dates import from_epoch_ms
from kaloricketabulky.sdk._numbers import parse_czech_number


def _coerce_epoch(value: object) -> object:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return from_epoch_ms(value)
    return value


def _coerce_czech_number(value: object) -> object:
    if isinstance(value, str):
        return parse_czech_number(value)
    return value


def _none_to_empty(value: object) -> object:
    return [] if value is None else value


EpochDateTime = Annotated[datetime | None, BeforeValidator(_coerce_epoch)]
CzechFloat = Annotated[float | None, BeforeValidator(_coerce_czech_number)]


class ApiModel(BaseModel):
    """Base model: accept camelCase aliases or snake_case names, ignore extras."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class Envelope[T](ApiModel):
    """The `{requestId, code, message, data}` wrapper around every response."""

    request_id: str | None = Field(default=None, alias="requestId")
    code: int
    message: str | None = None
    data: T


class MeasurementPoint(ApiModel):
    """A single dated measurement (weight, energy, drink, optional metric, ...)."""

    guid: str | None = None
    valid_from: EpochDateTime = Field(default=None, alias="from")
    valid_to: EpochDateTime = Field(default=None, alias="to")
    value: float | None = None
    value_string: str | None = Field(default=None, alias="valueString")
    description: str | None = None
    status: int | None = None
    system_time: EpochDateTime = Field(default=None, alias="systemTime")
    source: str | None = None


class WeekBar(ApiModel):
    """One day in a weekly bar chart (energy/drink/activity)."""

    title: str
    status: int
    value: float
