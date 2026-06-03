from datetime import date

from kaloricketabulky.sdk.models.summary import (
    DiarySummary,
    StatisticsSummary,
    SummaryItem,
)


def test_summary_item_parses_goal_and_keeps_display() -> None:
    item = SummaryItem.model_validate(
        {
            "title": None,
            "titleShort": None,
            "unit": "kcal",
            "goal": "2 384",
            "actual": "526",
            "percent": 22,
            "actualValue": 0.0,
            "code": "total",
        }
    )
    assert item.unit == "kcal"
    assert item.goal == "2 384"  # display preserved
    assert item.goal_value == 2384.0  # parsed
    assert item.percent == 22
    assert item.code == "total"


def test_diary_summary_parses_nested() -> None:
    summary = DiarySummary.model_validate(
        {
            "date": None,
            "items": [
                {"unit": "kcal", "goal": "2 384", "actual": "526", "percent": 22, "actualValue": 0.0, "code": "total"}
            ],
            "itemsDynamic": [
                [
                    {
                        "title": "Bílkoviny",
                        "unit": "g",
                        "goal": "147",
                        "actual": "30,4",
                        "percent": 20,
                        "actualValue": 30.4,
                        "code": "protein",
                    }
                ]
            ],
            "activityEnergyTotal": 434.0,
            "foodstuffEnergyTotal": 526.0,
            "weight": "85,2",
            "alcohol": "0",
            "nutrientsFromActivities": True,
            "mode": 0,
        }
    )
    assert summary.items[0].goal_value == 2384.0
    assert summary.items_dynamic[0][0].code == "protein"
    assert summary.weight == 85.2
    assert summary.alcohol == 0.0
    assert summary.nutrients_from_activities is True


def test_statistics_summary_parses_localized_and_weekbars() -> None:
    summary = StatisticsSummary.model_validate(
        {
            "date": "02.06.2026",
            "todayEnergy": "526",
            "todayEnergyTarget": "2 384",
            "energyUnit": "kcal",
            "energyUnitCode": "kcal",
            "todayDrink": "0,1",
            "drinkUnit": "l",
            "basal": "1 950",
            "amr": "1.0",
            "bmi": "27,8",
            "bmiCategory": "nadváha",
            "bmiRisk": "nízká",
            "mode": 0,
            "weekDate": "26.05.2026 - 01.06.2026",
            "weekEnergy": [{"title": "Út", "status": 0, "value": 129.58}],
            "weekDrink": [{"title": "Út", "status": 2, "value": 0.02}],
            "weekActivity": [{"title": "Út", "status": 0, "value": 2240.09}],
            "weight": "85,25",
            "weightTarget": "0",
            "weightUnit": "kg",
            "monthWeight": [{"guid": "w1", "from": 1780351200000, "value": 85.25}],
            "monthWeightTarget": [],
            "monthWeightMin": 85.25,
            "monthWeightMax": 85.25,
        }
    )
    assert summary.date == date(2026, 6, 2)
    assert summary.today_energy == 526.0
    assert summary.today_energy_target == 2384.0
    assert summary.basal == 1950.0
    assert summary.bmi == 27.8
    assert summary.bmi_category == "nadváha"
    assert summary.week_energy[0].value == 129.58
    assert summary.weight == 85.25
    assert summary.month_weight[0].value == 85.25
