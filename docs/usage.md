# Usage

## Authenticate

Construct a client and log in. `login` md5-hashes the password (as the API expects), checks the
response body for success, and stores the whole session — `JSESSIONID`, the locale cookie, and the
token — on the underlying HTTP client. Later requests reuse it.

```python
async with KaloricketabulkyClient() as client:
    await client.login("you@example.com", "password")
    ...
```

Wrong credentials raise `AuthError`. The session can expire; if a request starts failing, call
`login` again.

## Fetching data

All methods take `datetime.date` and return curated Pydantic models.

```python
from datetime import date
from kaloricketabulky.sdk import SnapshotType

diary   = await client.get_diary(date(2026, 6, 2))
streak  = await client.get_streak(date(2026, 6, 2))            # consecutive tracked days
tips    = await client.get_tips(date(2026, 5, 26), date(2026, 6, 1))
day     = await client.get_diary_summary(date(2026, 6, 2))
stats   = await client.get_statistics_summary(date(2026, 6, 2))
weight  = await client.get_snapshot(SnapshotType.WEIGHT, date(2025, 6, 2), date(2026, 6, 2))
custom  = await client.get_optional_snapshots(date(2025, 6, 2), date(2026, 6, 2))
```

`get_snapshot` accepts the single-series metrics (`ENERGY`, `NUTRIENTS`, `DRINK`, `WEIGHT`); the
optional (custom) metrics return a list and have their own method.

## Errors

Everything raised by the SDK derives from `KaloricError`:

- `AuthError` — login failed, or a request was rejected as unauthorized.
- `ApiError` — the response envelope carried a non-zero `code` (carries `.code` and the message).
- `KaloricError` — transport failures and non-JSON responses.

## Bringing your own HTTP client

Pass an `httpx.AsyncClient` to add timeouts, retries, or proxies. The SDK ships no retry logic
(to stay thin and to avoid hammering an unofficial API); supply a client for connection-level
retries:

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

A supplied client is **not** closed by `KaloricketabulkyClient` — manage its lifecycle yourself.
`login` (and any `Set-Cookie` the server sends) populates its cookie jar; that is how the session
is carried. A supplied client must set its own `base_url`.

## Command line

Set `KALORICKETABULKY_EMAIL` and `KALORICKETABULKY_PASSWORD` in your environment or a `.env` file,
then dump any endpoint as JSON:

```bash
uv run kaloricketabulky streak --date 2026-06-02
uv run kaloricketabulky diary --date 2026-06-02
uv run kaloricketabulky snapshot --metric weight --from 2025-06-02 --to 2026-06-02
```
