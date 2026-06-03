# kaloricketabulky-sdk

[![lint](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/lint.yml/badge.svg)](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/lint.yml)
[![pytest](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/pytest.yml/badge.svg)](https://github.com/tomasvotava/kaloricketabulky/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/tomasvotava/kaloricketabulky/branch/master/graph/badge.svg)](https://codecov.io/gh/tomasvotava/kaloricketabulky)
[![PyPI](https://img.shields.io/pypi/v/kaloricketabulky-sdk)](https://pypi.org/project/kaloricketabulky-sdk/)
![Python](https://img.shields.io/pypi/pyversions/kaloricketabulky-sdk)
![License](https://img.shields.io/github/license/tomasvotava/kaloricketabulky)

Typesafe, async, read-only access to the [kaloricketabulky.cz](https://www.kaloricketabulky.cz)
internal API. The SDK layer (`kaloricketabulky.sdk`) depends only on `httpx` and `pydantic` and
can be used on its own; the surrounding package adds configuration and a command-line entry point.

!!! warning "Unofficial — be a respectful guest"
    The site has no official public API; this is an unofficial client built against the endpoints
    the web app uses. Use it for your own data only, keep your polling slow and infrequent, and
    don't be a dick about it. If you get value out of
    [kaloricketabulky.cz](https://www.kaloricketabulky.cz), please
    [support them with a subscription](https://www.kaloricketabulky.cz/user/premium/public).

## Install

```bash
uv add kaloricketabulky-sdk
```

## At a glance

```python
import asyncio
from datetime import date

from kaloricketabulky.sdk import KaloricketabulkyClient, SnapshotType


async def main() -> None:
    async with KaloricketabulkyClient() as client:
        await client.login("you@example.com", "password")
        diary = await client.get_diary(date(2026, 6, 2))
        print(diary.energy_total)


asyncio.run(main())
```

See [Usage](usage.md) for the full surface, and the **API reference** in the navigation for every
model.
