import pytest

from kaloricketabulky.sdk._numbers import parse_czech_number


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("85,2", 85.2),
        ("2 384", 2384.0),  # regular-space thousands
        ("2\u00a0384", 2384.0),  # non-breaking-space thousands
        ("1\u2009000", 1000.0),  # thin-space thousands
        ("1.0", 1.0),  # amr uses a dot
        ("-0", 0.0),
        ("526", 526.0),
        ("0,06", 0.06),
    ],
)
def test_parse_czech_number_values(raw: str, expected: float) -> None:
    assert parse_czech_number(raw) == pytest.approx(expected)


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_parse_czech_number_blank_is_none(raw: str | None) -> None:
    assert parse_czech_number(raw) is None


def test_parse_czech_number_invalid_raises() -> None:
    with pytest.raises(ValueError, match="not a number"):
        parse_czech_number("abc")
