from kaloricketabulky import __version__
from kaloricketabulky.__main__ import main


def test_version_is_exposed() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_main_returns_success() -> None:
    assert main() == 0


async def test_async_runtime_is_available() -> None:
    async def echo(value: int) -> int:
        return value

    assert await echo(42) == 42
