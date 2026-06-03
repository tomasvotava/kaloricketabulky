import json
from datetime import date

import httpx
import pytest

from kaloricketabulky import __main__ as cli
from kaloricketabulky.sdk.client import KaloricketabulkyClient


def _envelope(data: object) -> httpx.Response:
    return httpx.Response(
        200,
        content=json.dumps({"requestId": None, "code": 0, "message": None, "data": data}),
    )


@pytest.fixture
def fake_client() -> KaloricketabulkyClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return _envelope(478)

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://example.test")
    return KaloricketabulkyClient(client=http)


def test_parse_args_streak() -> None:
    args = cli.parse_args(["streak", "--date", "2026-06-02"])
    assert args.command == "streak"
    assert args.date == date(2026, 6, 2)


async def test_run_streak_prints_json(capsys: pytest.CaptureFixture[str], fake_client: KaloricketabulkyClient) -> None:
    args = cli.parse_args(["streak", "--date", "2026-06-02"])
    await cli.run(args, client=fake_client)
    out = capsys.readouterr().out
    assert json.loads(out) == 478


def test_parse_args_tips() -> None:
    args = cli.parse_args(["tips", "--from", "2026-05-26", "--to", "2026-06-01"])
    assert args.command == "tips"
    assert args.date_from == date(2026, 5, 26)
    assert args.date_to == date(2026, 6, 1)


async def test_run_diary_summary_prints_json(capsys: pytest.CaptureFixture[str]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _envelope({"activityEnergyTotal": 123.0})

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://example.test")
    client = KaloricketabulkyClient(client=http)

    args = cli.parse_args(["diary-summary", "--date", "2026-06-02"])
    await cli.run(args, client=client)
    out = capsys.readouterr().out
    assert json.loads(out)["activity_energy_total"] == 123.0
