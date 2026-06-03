import json
from collections.abc import Callable

import httpx
import pytest

from kaloricketabulky.sdk.client import KaloricketabulkyClient
from kaloricketabulky.sdk.errors import ApiError, AuthError, KaloricError
from kaloricketabulky.sdk.models.snapshot import SnapshotType


def _envelope(data: object, code: int = 0, message: str | None = None) -> httpx.Response:
    body = {"requestId": None, "code": code, "message": message, "data": data}
    return httpx.Response(200, content=json.dumps(body))


def _client(
    handler: Callable[[httpx.Request], httpx.Response],
) -> KaloricketabulkyClient:
    transport = httpx.MockTransport(handler)
    http = httpx.AsyncClient(transport=transport, base_url="https://example.test")
    return KaloricketabulkyClient(client=http)


async def test_get_streak_sends_format() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["date"] = request.url.params.get("date")
        seen["format"] = request.url.params.get("format")
        return _envelope(478)

    from datetime import date

    async with _client(handler) as client:
        streak = await client.get_streak(date(2026, 6, 2))
    assert streak == 478
    assert seen["path"] == "/user/streak"
    assert seen["date"] == "2026-06-02"
    assert seen["format"] == "json"


async def test_get_diary_uses_dmy_path() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/user/diary/02.06.2026/get"
        return _envelope({"date": 1780351200000, "energyTotal": 526.0, "times": [], "activities": []})

    async with _client(handler) as client:
        diary = await client.get_diary(date(2026, 6, 2))
    assert diary.energy_total == 526.0


async def test_get_snapshot_path_and_optional_list() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        if "optional" in request.url.path:
            assert request.url.path == "/statistic/optional/01.06.2026/02.06.2026/get"
            return _envelope([{"type": "Obvod paže [cm]", "values": [], "tableData": []}])
        assert request.url.path == "/statistic/energy/01.06.2026/02.06.2026/get"
        return _envelope({"type": "energy", "values": [], "tableData": []})

    async with _client(handler) as client:
        snap = await client.get_snapshot(SnapshotType.ENERGY, date(2026, 6, 1), date(2026, 6, 2))
        optionals = await client.get_optional_snapshots(date(2026, 6, 1), date(2026, 6, 2))
    assert snap.type == "energy"
    assert optionals[0].type == "Obvod paže [cm]"


async def test_nonzero_code_raises_api_error() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        return _envelope(None, code=5, message="nope")

    async with _client(handler) as client:
        with pytest.raises(ApiError) as info:
            await client.get_streak(date(2026, 6, 2))
    assert info.value.code == 5


async def test_get_tips_path_param_and_parse() -> None:
    from datetime import date

    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["top"] = request.url.params.get("top")
        return _envelope([{"key": "protein_ok", "title": "Bílkoviny"}])

    async with _client(handler) as client:
        tips = await client.get_tips(date(2026, 5, 26), date(2026, 6, 1))
    assert seen["path"] == "/statistic/analysis/tips/26.05.2026/01.06.2026/get"
    assert seen["top"] == "true"
    assert tips[0].key == "protein_ok"


async def test_get_diary_summary_path() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/user/diary/summary/02.06.2026/get"
        return _envelope({"activityEnergyTotal": 123.0})

    async with _client(handler) as client:
        summary = await client.get_diary_summary(date(2026, 6, 2))
    assert summary.activity_energy_total == 123.0


async def test_get_statistics_summary_path() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/statistic/summary/02.06.2026/get"
        return _envelope({"todayEnergy": "526"})

    async with _client(handler) as client:
        summary = await client.get_statistics_summary(date(2026, 6, 2))
    assert summary.today_energy == 526.0


async def test_error_envelope_without_data_raises_api_error() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        body = {"requestId": None, "code": 5, "message": "nope"}
        return httpx.Response(200, content=json.dumps(body))

    async with _client(handler) as client:
        with pytest.raises(ApiError) as info:
            await client.get_streak(date(2026, 6, 2))
    assert info.value.code == 5


async def test_malformed_data_raises_kaloric_error() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        return _envelope("oops")

    async with _client(handler) as client:
        with pytest.raises(KaloricError):
            await client.get_diary(date(2026, 6, 2))


async def test_http_401_raises_auth_error() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    async with _client(handler) as client:
        with pytest.raises(AuthError):
            await client.get_streak(date(2026, 6, 2))


async def test_supplied_client_is_not_closed() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        return _envelope(478)

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://example.test")
    client = KaloricketabulkyClient(client=http)
    await client.get_streak(date(2026, 6, 2))
    await client.aclose()
    # A caller-supplied client is left open for the caller to manage.
    assert not http.is_closed
    await http.aclose()


async def test_owned_client_is_closed_on_aclose() -> None:
    client = KaloricketabulkyClient(base_url="https://example.test")
    internal = client._client
    await client.aclose()
    assert internal.is_closed


async def test_non_json_response_raises_kaloric_error() -> None:
    from datetime import date

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content="<html>not json</html>")

    async with _client(handler) as client:
        with pytest.raises(KaloricError):
            await client.get_streak(date(2026, 6, 2))
