import pytest

from kaloricketabulky.sdk.errors import ApiError, AuthError, KaloricError


def test_hierarchy() -> None:
    assert issubclass(ApiError, KaloricError)
    assert issubclass(AuthError, KaloricError)


def test_api_error_carries_code_and_message() -> None:
    err = ApiError(7, "boom")
    assert err.code == 7
    assert err.api_message == "boom"
    assert "7" in str(err)
    with pytest.raises(KaloricError):
        raise err
