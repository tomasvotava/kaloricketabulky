from kaloricketabulky import __version__


def test_version_is_exposed() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_cli_parses_streak() -> None:
    from datetime import date

    from kaloricketabulky.__main__ import parse_args

    args = parse_args(["streak", "--date", "2026-06-02"])
    assert args.command == "streak"
    assert args.date == date(2026, 6, 2)


async def test_async_runtime_is_available() -> None:
    async def echo(value: int) -> int:
        return value

    assert await echo(42) == 42
