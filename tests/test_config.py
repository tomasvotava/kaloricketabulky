import pytest
from env_proxy import EnvProxyError

from kaloricketabulky.config import Settings


def test_settings_reads_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KALORICKETABULKY_EMAIL", "a@b.cz")
    monkeypatch.setenv("KALORICKETABULKY_PASSWORD", "pw")
    monkeypatch.setenv("KALORICKETABULKY_BASE_URL", "https://example.test")
    assert Settings.email == "a@b.cz"
    assert Settings.password == "pw"  # noqa: S105 — fake credential fixture, not a secret
    assert Settings.base_url == "https://example.test"


def test_settings_missing_required_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KALORICKETABULKY_EMAIL", raising=False)
    with pytest.raises(EnvProxyError):
        _ = Settings.email


def test_settings_base_url_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KALORICKETABULKY_BASE_URL", raising=False)
    assert Settings.base_url == "https://www.kaloricketabulky.cz"
