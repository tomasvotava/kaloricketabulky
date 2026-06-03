"""Authenticate an HTTP client by logging in with email and password."""

from hashlib import md5

import httpx

from kaloricketabulky.sdk.errors import AuthError

DEFAULT_BASE_URL = "https://www.kaloricketabulky.cz"
LOGIN_PATH = "/login/create"
TOKEN_COOKIE = "kaloricketabulky_token"  # noqa: S105 - cookie name, not a credential


async def login(client: httpx.AsyncClient, email: str, password: str) -> None:
    """Log in on `client`, leaving the session cookies in its cookie jar.

    The endpoint answers 200 even on bad credentials, signalling failure through a
    non-zero `code` in the JSON body, so the body is checked rather than the status.
    The password is sent md5-hashed, as the API expects. Raises AuthError on a failed
    or unparseable login.
    """
    try:
        response = await client.post(
            LOGIN_PATH,
            params={"format": "json", "voucher": "false"},
            json={"email": email, "password": md5(password.encode("utf-8")).hexdigest()},  # noqa: S324 - API requires md5
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AuthError(f"login request failed: {exc}") from exc
    try:
        body = response.json()
    except ValueError as exc:
        raise AuthError(f"login response was not JSON: {exc}") from exc
    if body.get("code") != 0:
        raise AuthError(body.get("message") or f"login failed with code {body.get('code')}")
    if TOKEN_COOKIE not in client.cookies:
        raise AuthError("login succeeded but set no session cookie")
