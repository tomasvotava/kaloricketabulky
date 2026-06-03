import json
from collections.abc import Callable
from hashlib import md5

import httpx
import pytest

from kaloricketabulky.sdk.auth import TOKEN_COOKIE, login
from kaloricketabulky.sdk.errors import AuthError

_LOGIN_COOKIES = [
    ("set-cookie", "JSESSIONID=sess; Path=/"),
    ("set-cookie", f"{TOKEN_COOKIE}=tok123; Path=/"),
    ("set-cookie", "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=cs; Path=/"),
]


def _ok_login(extra_headers: list[tuple[str, str]] | None = None) -> httpx.Response:
    body = {"requestId": None, "code": 0, "message": None, "data": None}
    headers = extra_headers if extra_headers is not None else _LOGIN_COOKIES
    return httpx.Response(200, headers=headers, content=json.dumps(body))


def _mock(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://x.test")


async def test_login_stores_all_session_cookies() -> None:
    async with _mock(lambda r: _ok_login()) as http:
        await login(http, "a@b.cz", "pw")
        assert TOKEN_COOKIE in http.cookies
        assert http.cookies["JSESSIONID"] == "sess"
        assert http.cookies["org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE"] == "cs"


async def test_login_sends_md5_hashed_password() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["password"] = json.loads(request.content)["password"]
        return _ok_login()

    async with _mock(handler) as http:
        await login(http, "a@b.cz", "secret")
    assert seen["password"] == md5(b"secret").hexdigest()  # noqa: S324 - asserts the API's required hashing


async def test_login_nonzero_code_raises_with_message() -> None:
    body = {"requestId": None, "code": 4, "message": "Zadané heslo nebo e-mail není správné", "data": None}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=json.dumps(body))

    async with _mock(handler) as http:
        with pytest.raises(AuthError, match="není správné"):
            await login(http, "a@b.cz", "wrong")


async def test_login_without_session_cookie_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _ok_login(extra_headers=[])  # code 0 but no Set-Cookie

    async with _mock(handler) as http:
        with pytest.raises(AuthError, match="session cookie"):
            await login(http, "a@b.cz", "pw")
