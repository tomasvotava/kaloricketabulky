from datetime import date, datetime

from kaloricketabulky.sdk.models.common import (
    Envelope,
    MeasurementPoint,
    WeekBar,
)


def test_envelope_parses_alias_and_data() -> None:
    env = Envelope[int].model_validate({"requestId": None, "code": 0, "message": None, "data": 478})
    assert env.request_id is None
    assert env.code == 0
    assert env.data == 478


def test_measurement_point_converts_epoch_and_aliases() -> None:
    point = MeasurementPoint.model_validate(
        {
            "guid": "abc",
            "from": 1780351200000,
            "to": None,
            "value": 85.25,
            "valueString": "85,2",
            "description": "02.06.26",
            "status": None,
            "systemTime": None,
            "source": None,
        }
    )
    assert point.guid == "abc"
    assert point.valid_from is not None
    assert point.valid_from.date() == date(2026, 6, 2)
    assert isinstance(point.valid_from, datetime)
    assert point.valid_to is None
    assert point.value == 85.25
    assert point.value_string == "85,2"


def test_week_bar() -> None:
    bar = WeekBar.model_validate({"title": "Út", "status": 0, "value": 129.58})
    assert bar.title == "Út"
    assert bar.status == 0
    assert bar.value == 129.58
