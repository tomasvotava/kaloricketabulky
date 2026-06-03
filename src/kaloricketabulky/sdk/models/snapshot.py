"""Long-term statistic snapshots (energy, nutrients, drink, weight, optional)."""

from enum import StrEnum
from typing import Annotated

from pydantic import BeforeValidator, Field

from kaloricketabulky.sdk.models.common import (
    ApiModel,
    EpochDateTime,
    MeasurementPoint,
    _none_to_empty,
)

_PointList = Annotated[list[MeasurementPoint], BeforeValidator(_none_to_empty)]


class SnapshotType(StrEnum):
    """The statistic kind requested from `/statistic/{type}/.../get`."""

    ENERGY = "energy"
    NUTRIENTS = "nutrients"
    DRINK = "drink"
    WEIGHT = "weight"
    OPTIONAL = "optional"


class SnapshotTableRow(ApiModel):
    """A value/target pair as shown in the snapshot table."""

    value: MeasurementPoint | None = None
    target: MeasurementPoint | None = None


class NutrientsPoint(ApiModel):
    """A dated fat/protein/carbs triplet (nutrients snapshot)."""

    created_date: EpochDateTime = Field(default=None, alias="createdDate")
    fat: MeasurementPoint | None = None
    protein: MeasurementPoint | None = None
    carbs: MeasurementPoint | None = None


class NutrientsTableRow(ApiModel):
    """Value/target macro pairs as shown in the nutrients snapshot table."""

    fat_target: MeasurementPoint | None = Field(default=None, alias="fatTarget")
    protein_target: MeasurementPoint | None = Field(default=None, alias="proteinTarget")
    carbs_target: MeasurementPoint | None = Field(default=None, alias="carbsTarget")
    fat_value: MeasurementPoint | None = Field(default=None, alias="fatValue")
    protein_value: MeasurementPoint | None = Field(default=None, alias="proteinValue")
    carbs_value: MeasurementPoint | None = Field(default=None, alias="carbsValue")


class Snapshot(ApiModel):
    """One statistic series over a date range.

    Flat metrics (energy/drink/weight) use `values`/`target`/`table_data`; the
    nutrients metric uses the `nutrients_*` triplets instead. The `type` field is
    the metric name, or the custom metric label for optional snapshots.
    """

    type: str
    unit: str | None = None
    valid_from: EpochDateTime = Field(default=None, alias="from")
    valid_to: EpochDateTime = Field(default=None, alias="to")
    guid: str | None = None
    min: float | None = None
    max: float | None = None
    values: _PointList = Field(default_factory=list)
    target: _PointList = Field(default_factory=list)
    table_data: list[SnapshotTableRow] = Field(default_factory=list, alias="tableData")
    nutrients_values: list[NutrientsPoint] = Field(default_factory=list, alias="nutrientsValues")
    nutrients_target: list[NutrientsPoint] = Field(default_factory=list, alias="nutrientsTarget")
    nutrients_table_data: list[NutrientsTableRow] = Field(default_factory=list, alias="nutrientsTableData")
