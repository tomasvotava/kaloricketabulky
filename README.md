# kaloricketabulky-sdk

[![lint](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/lint.yml/badge.svg)](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/lint.yml)
[![pytest](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/pytest.yml/badge.svg)](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/tomasvotava/kaloricketabulky/branch/master/graph/badge.svg)](https://codecov.io/gh/tomasvotava/kaloricketabulky)
[![PyPI](https://img.shields.io/pypi/v/kaloricketabulky-sdk)](https://pypi.org/project/kaloricketabulky-sdk/)
![Python](https://img.shields.io/pypi/pyversions/kaloricketabulky-sdk)
![License](https://img.shields.io/github/license/tomasvotava/kaloricketabulky)
[![Docs](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/docs.yml/badge.svg)](https://tomasvotava.github.io/kaloricketabulky/)

Typesafe, async, read-only access to the [kaloricketabulky.cz](https://www.kaloricketabulky.cz)
internal API. The SDK layer (`kaloricketabulky.sdk`) is self-contained and usable on its own;
the surrounding package adds configuration and a command-line entry point.

> The site has no official public API. This is an unofficial client built against the
> endpoints the web app uses. Use it for your own data only, be a respectful guest:
> don't hammer the site with requests, keep your polling slow and infrequent, and don't
> be a dick about it.
>
> If you get value out of [kaloricketabulky.cz](https://www.kaloricketabulky.cz), please
> consider [supporting them with a subscription](https://www.kaloricketabulky.cz/user/premium/public).

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv add kaloricketabulky-sdk
```

## Usage

```python
import asyncio
from datetime import date

from kaloricketabulky.sdk import KaloricketabulkyClient, SnapshotType


async def main() -> None:
    async with KaloricketabulkyClient() as client:
        await client.login("you@example.com", "password")

        diary = await client.get_diary(date(2026, 6, 2))
        streak = await client.get_streak(date(2026, 6, 2))
        weight = await client.get_snapshot(SnapshotType.WEIGHT, date(2025, 6, 2), date(2026, 6, 2))
        print(diary.energy_total, streak, weight.min, weight.max)


asyncio.run(main())
```

`login` stores the session cookies on the underlying HTTP client and later requests reuse them.
The session can expire; if a request starts failing, call `login` again.

### CLI

Set `KALORICKETABULKY_EMAIL` + `KALORICKETABULKY_PASSWORD` in your environment or a `.env` file,
then:

```bash
uv run kaloricketabulky streak --date 2026-06-02
uv run kaloricketabulky diary --date 2026-06-02
uv run kaloricketabulky snapshot --metric weight --from 2025-06-02 --to 2026-06-02
```

### Retries

The SDK ships no retry logic, to stay thin and to avoid hammering an unofficial API. To add
retries or backoff, inject your own client — for example connection-level retries:

```python
import httpx
from kaloricketabulky.sdk import KaloricketabulkyClient

async with httpx.AsyncClient(
    base_url="https://www.kaloricketabulky.cz",
    transport=httpx.AsyncHTTPTransport(retries=3),
) as http:
    client = KaloricketabulkyClient(client=http)
    await client.login("you@example.com", "password")
    ...
```

A supplied client is not closed by `KaloricketabulkyClient` — manage its lifecycle yourself (e.g.
`async with`). Note that `login` (and any `Set-Cookie` the server returns) populates the client's
cookie jar; that is how the session is carried. A supplied client must set its own `base_url`;
the `base_url=` argument applies only when `KaloricketabulkyClient` creates its own HTTP client.
Unsure which URL? Reuse `Settings.base_url` from `kaloricketabulky.config`.

## Development

```bash
uv sync                      # create the environment from the lockfile
uv run pytest                # run tests with coverage
uv run ruff format --check . # check formatting
uv run ruff check .          # lint
uv run mypy src tests        # strict type-check
```

## Layout

```
src/kaloricketabulky/
    __init__.py    package version
    __main__.py    command-line entry point (`kaloricketabulky`)
    sdk/           standalone read-only SDK (httpx + pydantic only)
tests/             test suite
```

## Releases

Versioning and the changelog are driven by [Commitizen](https://commitizen-tools.github.io/commitizen/).
Do not edit `CHANGELOG.md` by hand:

```bash
uv run cz bump
```

## License

MIT
