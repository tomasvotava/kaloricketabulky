import json
from pathlib import Path

from kaloricketabulky.sdk.models.common import Envelope
from kaloricketabulky.sdk.models.diary import Diary
from kaloricketabulky.sdk.models.snapshot import Snapshot
from kaloricketabulky.sdk.models.summary import DiarySummary, StatisticsSummary
from kaloricketabulky.sdk.models.tips import Tip

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _load(name: str) -> dict[str, object]:
    data: dict[str, object] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return data


def test_diary_fixture() -> None:
    env = Envelope[Diary].model_validate(_load("user_diary.json"))
    assert env.code == 0
    assert isinstance(env.data, Diary)


def test_tips_fixture() -> None:
    env = Envelope[list[Tip]].model_validate(_load("user_tips.json"))
    assert all(isinstance(t, Tip) for t in env.data)


def test_diary_summary_fixture() -> None:
    env = Envelope[DiarySummary].model_validate(_load("diary_summary.json"))
    assert isinstance(env.data, DiarySummary)


def test_stats_summary_fixture() -> None:
    env = Envelope[StatisticsSummary].model_validate(_load("stats_summary.json"))
    assert isinstance(env.data, StatisticsSummary)


def test_single_snapshot_fixtures() -> None:
    for name in ["snap_energy.json", "snap_drink.json", "snap_weight.json", "snap_nutrients.json"]:
        env = Envelope[Snapshot].model_validate(_load(name))
        assert isinstance(env.data, Snapshot)


def test_optional_snapshot_fixture() -> None:
    env = Envelope[list[Snapshot]].model_validate(_load("snap_optional.json"))
    assert all(isinstance(s, Snapshot) for s in env.data)
