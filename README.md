# kaloricketabulky-sdk

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
