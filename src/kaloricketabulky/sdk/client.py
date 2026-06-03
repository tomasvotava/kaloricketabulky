"""Async read-only client for the kaloricketabulky.cz internal API."""

from contextlib import AsyncExitStack
from datetime import date
from types import TracebackType
from typing import Literal, TypeVar

import httpx
from pydantic import ValidationError

from kaloricketabulky.sdk import auth
from kaloricketabulky.sdk._dates import format_path_date, format_query_date
from kaloricketabulky.sdk.errors import ApiError, AuthError, KaloricError
from kaloricketabulky.sdk.models.common import ApiModel, Envelope
from kaloricketabulky.sdk.models.diary import Diary
from kaloricketabulky.sdk.models.snapshot import Snapshot, SnapshotType
from kaloricketabulky.sdk.models.summary import DiarySummary, StatisticsSummary
from kaloricketabulky.sdk.models.tips import Tip

DEFAULT_BASE_URL = auth.DEFAULT_BASE_URL
DEFAULT_TIMEOUT = 30.0

# The snapshot metrics that return a single series; `optional` returns a list and
# has its own method, so it is excluded here to make misuse a static type error.
SingleSnapshotType = Literal[
    SnapshotType.ENERGY,
    SnapshotType.NUTRIENTS,
    SnapshotType.DRINK,
    SnapshotType.WEIGHT,
]

T = TypeVar("T")


class _ResponseStatus(ApiModel):
    """Reads the envelope status without requiring a particular `data` shape."""

    code: int
    message: str | None = None


class KaloricketabulkyClient:
    """Async client returning curated models. Call `login` before fetching data."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._client = client if client is not None else httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._stack = AsyncExitStack()
        if client is None:
            # We created the client, so we close it on aclose(); a supplied one is left open.
            self._stack.push_async_callback(self._client.aclose)

    async def login(self, email: str, password: str) -> None:
        """Authenticate; the session cookies are stored on the underlying HTTP client.

        Subsequent requests reuse them. If the session later expires, catch the error
        and call this again.
        """
        await auth.login(self._client, email, password)

    async def __aenter__(self) -> "KaloricketabulkyClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the HTTP client if this instance created it; leave a supplied one open."""
        await self._stack.aclose()

    async def _get(self, path: str, type_: type[T], *, params: dict[str, str] | None = None) -> T:
        query = {"format": "json", **(params or {})}
        try:
            response = await self._client.get(path, params=query)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                raise AuthError(f"request to {path} was not authorized") from exc
            raise KaloricError(f"request to {path} failed: {exc}") from exc
        except httpx.HTTPError as exc:
            raise KaloricError(f"request to {path} failed: {exc}") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise KaloricError(f"response from {path} was not JSON: {exc}") from exc
        try:
            status = _ResponseStatus.model_validate(payload)
        except ValidationError as exc:
            raise KaloricError(f"unexpected response from {path}: {exc}") from exc
        if status.code != 0:
            raise ApiError(status.code, status.message)
        try:
            # `Envelope[type_]` is itself a Pydantic model class (Pydantic caches the
            # parametrization and its validator), so validate against it directly.
            envelope = Envelope[type_].model_validate(payload)  # type: ignore[valid-type]
        except ValidationError as exc:
            raise KaloricError(f"could not parse data from {path}: {exc}") from exc
        return envelope.data

    async def get_diary(self, day: date) -> Diary:
        """Fetch the diary (meals, activities, totals) for a day."""
        return await self._get(f"/user/diary/{format_path_date(day)}/get", Diary)

    async def get_tips(self, date_from: date, date_to: date) -> list[Tip]:
        """Fetch analysis tips for a date range."""
        path = f"/statistic/analysis/tips/{format_path_date(date_from)}/{format_path_date(date_to)}/get"
        return await self._get(path, list[Tip], params={"top": "true"})

    async def get_streak(self, day: date) -> int:
        """Fetch the number of consecutive days tracked up to `day`."""
        return await self._get("/user/streak", int, params={"date": format_query_date(day)})

    async def get_diary_summary(self, day: date) -> DiarySummary:
        """Fetch the diary summary for a day."""
        return await self._get(f"/user/diary/summary/{format_path_date(day)}/get", DiarySummary)

    async def get_statistics_summary(self, day: date) -> StatisticsSummary:
        """Fetch the statistics summary for a day."""
        return await self._get(f"/statistic/summary/{format_path_date(day)}/get", StatisticsSummary)

    async def get_snapshot(self, metric: SingleSnapshotType, date_from: date, date_to: date) -> Snapshot:
        """Fetch a single-series snapshot (energy, nutrients, drink, or weight).

        `metric` excludes the optional series at the type level; use
        `get_optional_snapshots` for that.
        """
        path = f"/statistic/{metric.value}/{format_path_date(date_from)}/{format_path_date(date_to)}/get"
        return await self._get(path, Snapshot)

    async def get_optional_snapshots(self, date_from: date, date_to: date) -> list[Snapshot]:
        """Fetch all optional (custom) metric snapshots for a date range."""
        path = f"/statistic/optional/{format_path_date(date_from)}/{format_path_date(date_to)}/get"
        return await self._get(path, list[Snapshot])
