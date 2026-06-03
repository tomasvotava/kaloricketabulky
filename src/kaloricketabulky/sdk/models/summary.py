"""Daily diary summary and statistics summary."""

from datetime import date as date_

from pydantic import Field, computed_field, field_validator

from kaloricketabulky.sdk._dates import parse_dmy
from kaloricketabulky.sdk._numbers import parse_czech_number
from kaloricketabulky.sdk.models.common import (
    ApiModel,
    CzechFloat,
    MeasurementPoint,
    WeekBar,
)


class SummaryItem(ApiModel):
    """A goal/actual progress row. Display strings are kept; goal exposes a parsed value."""

    title: str | None = None
    title_short: str | None = Field(default=None, alias="titleShort")
    unit: str | None = None
    goal: str | None = None
    actual: str | None = None
    percent: int | None = None
    actual_value: float | None = Field(default=None, alias="actualValue")
    code: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def goal_value(self) -> float | None:
        """The `goal` display string parsed to a float."""
        return parse_czech_number(self.goal)


class DiaryBalance(ApiModel):
    """Energy in/out breakdown (localized number strings parsed to floats)."""

    energy_output_total: CzechFloat = Field(default=None, alias="energyOutputTotal")
    energy_intake_maintenance: CzechFloat = Field(default=None, alias="energyIntakeMaintenance")
    energy_deficit: CzechFloat = Field(default=None, alias="energyDeficit")
    target: CzechFloat = None
    basal: CzechFloat = None
    intake: CzechFloat = None
    intake_percent: CzechFloat = Field(default=None, alias="intakePercent")
    intake_rest: CzechFloat = Field(default=None, alias="intakeRest")
    intake_rest_percent: CzechFloat = Field(default=None, alias="intakeRestPercent")
    output: CzechFloat = None
    digestion: bool | None = None
    consider_activity: bool | None = Field(default=None, alias="considerActivity")
    own_target: bool | None = Field(default=None, alias="ownTarget")
    own_target_value: float | None = Field(default=None, alias="ownTargetValue")


class DiarySummary(ApiModel):
    """The diary summary endpoint: progress items plus daily roll-ups."""

    items: list[SummaryItem] = Field(default_factory=list)
    items_dynamic: list[list[SummaryItem]] = Field(default_factory=list, alias="itemsDynamic")
    activity_energy_total: float | None = Field(default=None, alias="activityEnergyTotal")
    foodstuff_energy_total: float | None = Field(default=None, alias="foodstuffEnergyTotal")
    weight: CzechFloat = None
    alcohol: CzechFloat = None
    nutrients_from_activities: bool | None = Field(default=None, alias="nutrientsFromActivities")
    mode: int | None = None
    balance: DiaryBalance | None = None


class StatisticsSummary(ApiModel):
    """The statistics summary: today's figures, weekly bars, and month weight."""

    date: date_ | None = None
    today_energy: CzechFloat = Field(default=None, alias="todayEnergy")
    today_energy_target: CzechFloat = Field(default=None, alias="todayEnergyTarget")
    energy_unit: str | None = Field(default=None, alias="energyUnit")
    energy_unit_code: str | None = Field(default=None, alias="energyUnitCode")
    today_drink: CzechFloat = Field(default=None, alias="todayDrink")
    today_drink_target: CzechFloat = Field(default=None, alias="todayDrinkTarget")
    drink_unit: str | None = Field(default=None, alias="drinkUnit")
    today_activity: CzechFloat = Field(default=None, alias="todayActivity")
    basal: CzechFloat = None
    amr: CzechFloat = None
    amr_energy: CzechFloat = Field(default=None, alias="amrEnergy")
    bmi: CzechFloat = None
    bmi_category: str | None = Field(default=None, alias="bmiCategory")
    bmi_risk: str | None = Field(default=None, alias="bmiRisk")
    mode: int | None = None
    week_date: str | None = Field(default=None, alias="weekDate")
    week_energy: list[WeekBar] = Field(default_factory=list, alias="weekEnergy")
    week_drink: list[WeekBar] = Field(default_factory=list, alias="weekDrink")
    week_activity: list[WeekBar] = Field(default_factory=list, alias="weekActivity")
    weight: CzechFloat = None
    weight_target: CzechFloat = Field(default=None, alias="weightTarget")
    weight_unit: str | None = Field(default=None, alias="weightUnit")
    month_weight: list[MeasurementPoint] = Field(default_factory=list, alias="monthWeight")
    month_weight_target: list[MeasurementPoint] = Field(default_factory=list, alias="monthWeightTarget")
    month_weight_min: float | None = Field(default=None, alias="monthWeightMin")
    month_weight_max: float | None = Field(default=None, alias="monthWeightMax")

    @field_validator("date", mode="before")
    @classmethod
    def _parse_date(cls, value: object) -> object:
        return parse_dmy(value) if isinstance(value, str) else value
