"""Command-line entry point: fetch data and print it as JSON."""

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date as date_
from datetime import datetime

from env_proxy import EnvProxyError

from kaloricketabulky.config import Settings
from kaloricketabulky.sdk._dates import PRAGUE
from kaloricketabulky.sdk.client import KaloricketabulkyClient
from kaloricketabulky.sdk.errors import KaloricError
from kaloricketabulky.sdk.models.snapshot import SnapshotType


@dataclass(frozen=True)
class Args:
    """Parsed CLI arguments. Each command populates the fields it needs."""

    command: str
    date: date_ | None = None
    date_from: date_ | None = None
    date_to: date_ | None = None
    metric: SnapshotType | None = None


def _parse_date(value: str) -> date_:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=PRAGUE).date()


def _require[T](value: T | None, name: str) -> T:
    """Return a value argparse guaranteed is present, narrowing it from optional."""
    if value is None:
        raise ValueError(f"missing required argument: {name}")
    return value


def parse_args(argv: Sequence[str] | None = None) -> Args:
    """Parse CLI arguments into a typed Args."""
    parser = argparse.ArgumentParser(prog="kaloricketabulky", description="Fetch your data as JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    streak = sub.add_parser("streak", help="Consecutive tracked days.")
    streak.add_argument("--date", type=_parse_date, required=True)

    diary = sub.add_parser("diary", help="Day diary.")
    diary.add_argument("--date", type=_parse_date, required=True)

    snapshot = sub.add_parser("snapshot", help="A statistic snapshot over a range.")
    snapshot.add_argument("--metric", type=SnapshotType, choices=list(SnapshotType), required=True)
    snapshot.add_argument("--from", dest="date_from", type=_parse_date, required=True)
    snapshot.add_argument("--to", dest="date_to", type=_parse_date, required=True)

    tips = sub.add_parser("tips", help="Analysis tips over a range.")
    tips.add_argument("--from", dest="date_from", type=_parse_date, required=True)
    tips.add_argument("--to", dest="date_to", type=_parse_date, required=True)

    diary_summary = sub.add_parser("diary-summary", help="Day diary summary.")
    diary_summary.add_argument("--date", type=_parse_date, required=True)

    statistics_summary = sub.add_parser("statistics-summary", help="Day statistics summary.")
    statistics_summary.add_argument("--date", type=_parse_date, required=True)

    return Args(**vars(parser.parse_args(argv)))


async def _fetch(args: Args, client: KaloricketabulkyClient) -> object:
    if args.command == "streak":
        return await client.get_streak(_require(args.date, "date"))
    if args.command == "diary":
        return (await client.get_diary(_require(args.date, "date"))).model_dump(mode="json")
    if args.command == "snapshot":
        metric = _require(args.metric, "metric")
        date_from = _require(args.date_from, "from")
        date_to = _require(args.date_to, "to")
        if metric is SnapshotType.OPTIONAL:
            data = await client.get_optional_snapshots(date_from, date_to)
            return [s.model_dump(mode="json") for s in data]
        # mypy narrows `metric` to the non-optional members here, matching get_snapshot's type.
        return (await client.get_snapshot(metric, date_from, date_to)).model_dump(mode="json")
    if args.command == "tips":
        tips = await client.get_tips(_require(args.date_from, "from"), _require(args.date_to, "to"))
        return [t.model_dump(mode="json") for t in tips]
    if args.command == "diary-summary":
        return (await client.get_diary_summary(_require(args.date, "date"))).model_dump(mode="json")
    if args.command == "statistics-summary":
        return (await client.get_statistics_summary(_require(args.date, "date"))).model_dump(mode="json")
    raise ValueError(f"unknown command: {args.command}")


async def run(args: Args, *, client: KaloricketabulkyClient) -> int:
    """Execute a parsed command against the client and print JSON to stdout."""
    result = await _fetch(args, client)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")
    return 0


async def _build_client() -> KaloricketabulkyClient:
    # Settings.email/password are required; env-proxy raises if they are unset.
    client = KaloricketabulkyClient(base_url=Settings.base_url)
    await client.login(Settings.email, Settings.password)
    return client


async def _main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    client = await _build_client()
    try:
        return await run(args, client=client)
    finally:
        await client.aclose()


def main() -> int:
    """Console-script entry point."""
    try:
        return asyncio.run(_main())
    except (KaloricError, EnvProxyError) as exc:
        # KaloricError covers AuthError; EnvProxyError covers a missing required setting.
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
