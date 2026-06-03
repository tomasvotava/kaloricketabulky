"""The day diary: meals of foodstuffs, logged activities, and daily totals."""

from pydantic import Field

from kaloricketabulky.sdk.models.common import ApiModel, CzechFloat, EpochDateTime


class DiaryItem(ApiModel):
    """Shared shape of a diary entry (foodstuff and activity use the same fields)."""

    id: str
    type: str
    guid_type: str | None = Field(default=None, alias="guidType")
    title: str | None = None
    unit: str | None = None
    url: str | None = None
    status: int | None = None
    energy: CzechFloat = None
    energy_unit: str | None = Field(default=None, alias="energyUnit")
    protein: float | None = None
    carbohydrate: float | None = None
    fat: float | None = None
    fiber: float | None = None
    sugar: float | None = None
    salt: float | None = None
    saturated_fatty_acid: float | None = Field(default=None, alias="saturatedFattyAcid")
    trans_fatty_acid: float | None = Field(default=None, alias="transFattyAcid")
    mono_saturated: float | None = Field(default=None, alias="monoSaturated")
    poly_saturated: float | None = Field(default=None, alias="polySaturated")
    cholesterol: float | None = None
    sodium: float | None = None
    calcium: float | None = None
    phe: float | None = None
    alcohol: float | None = None
    water: float | None = None


class DiaryFoodstuff(DiaryItem):
    """A food entry within a meal."""


class DiaryActivity(DiaryItem):
    """A logged physical activity (burns energy; may carry a step count)."""

    activity_type: int | None = Field(default=None, alias="activityType")
    steps: float | None = None


class Meal(ApiModel):
    """A named meal slot (e.g. Snídaně) holding its foodstuffs."""

    id: str
    title: str | None = None
    items: list[DiaryFoodstuff] = Field(default_factory=list, alias="foodstuff")


class Diary(ApiModel):
    """A single day's diary: meals, activities, and rolled-up totals."""

    date: EpochDateTime = None
    energy_unit: str | None = Field(default=None, alias="energyUnit")
    energy_total: float | None = Field(default=None, alias="energyTotal")
    energy_plus: float | None = Field(default=None, alias="energyPlus")
    energy_minus: float | None = Field(default=None, alias="energyMinus")
    protein_total: float | None = Field(default=None, alias="proteinTotal")
    carbohydrate_total: float | None = Field(default=None, alias="carbohydrateTotal")
    fat_total: float | None = Field(default=None, alias="fatTotal")
    fiber_total: float | None = Field(default=None, alias="fiberTotal")
    sugar_total: float | None = Field(default=None, alias="sugarTotal")
    salt_total: float | None = Field(default=None, alias="saltTotal")
    saturated_fatty_acid_total: float | None = Field(default=None, alias="saturatedFattyAcidTotal")
    calcium_total: float | None = Field(default=None, alias="calciumTotal")
    phe_total: float | None = Field(default=None, alias="pheTotal")
    foodstuff_count: int | None = Field(default=None, alias="foodstuffCount")
    drink_regime: float | None = Field(default=None, alias="drinkRegime")
    meals: list[Meal] = Field(default_factory=list, alias="times")
    activities: list[DiaryActivity] = Field(default_factory=list)
