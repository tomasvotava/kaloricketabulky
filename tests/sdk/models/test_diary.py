from datetime import date

from kaloricketabulky.sdk.models.diary import Diary, DiaryActivity, DiaryFoodstuff


def _foodstuff(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "095b74fbbf414b35a3863654046b405b",
        "type": "foodstuff",
        "guidType": "d10ffdda00be195b",
        "title": "banán",
        "unit": "2 x kus (90 g)",
        "energy": "169",
        "energyUnit": "kcal",
        "protein": 2.16,
        "carbohydrate": 39.6,
        "fat": 0.36,
        "fiber": 3.6,
        "sugar": 34.2,
        "salt": 0.0,
        "calcium": 0.0216,
        "phe": 0.108,
        "water": 133.02,
        "url": "banan",
        # UI noise that must be dropped:
        "open": False,
        "showInfo": False,
        "favorite": True,
        "editableUnit": True,
    }
    base.update(overrides)
    return base


def test_foodstuff_parses_and_drops_ui_fields() -> None:
    item = DiaryFoodstuff.model_validate(_foodstuff())
    assert item.id == "095b74fbbf414b35a3863654046b405b"
    assert item.type == "foodstuff"
    assert item.title == "banán"
    assert item.energy == 169.0  # parsed from the "169" string
    assert item.protein == 2.16
    assert not hasattr(item, "open")
    assert not hasattr(item, "favorite")


def test_activity_parses_activity_fields() -> None:
    activity = DiaryActivity.model_validate(
        {
            "id": "dba9ea9472c540a1aa66bd6e27c6b6a8",
            "type": "activity",
            "title": "Garmin aktivita (Silový trénink)",
            "unit": "73 min",
            "energy": "434",
            "energyUnit": "kcal",
            "activityType": 6,
            "steps": 722.0,
        }
    )
    assert activity.type == "activity"
    assert activity.energy == 434.0
    assert activity.activity_type == 6
    assert activity.steps == 722.0


def test_diary_parses_meals_and_totals() -> None:
    diary = Diary.model_validate(
        {
            "date": 1780351200000,
            "energyUnit": "kcal",
            "energyTotal": 526.0,
            "proteinTotal": 30.4,
            "carbohydrateTotal": 87.3,
            "fatTotal": 7.3,
            "foodstuffCount": 7,
            "drinkRegime": 0.06,
            "times": [
                {"id": "1", "title": "Snídaně", "foodstuff": [_foodstuff()]},
                {"id": "2", "title": "Oběd", "foodstuff": []},
            ],
            "activities": [{"id": "a1", "type": "activity", "title": "Běh", "energy": "434", "steps": 722.0}],
        }
    )
    assert diary.date is not None
    assert diary.date.date() == date(2026, 6, 2)
    assert diary.energy_total == 526.0
    assert diary.foodstuff_count == 7
    assert len(diary.meals) == 2
    assert diary.meals[0].title == "Snídaně"
    assert diary.meals[0].items[0].title == "banán"
    assert diary.meals[1].items == []
    assert len(diary.activities) == 1
    assert diary.activities[0].steps == 722.0
