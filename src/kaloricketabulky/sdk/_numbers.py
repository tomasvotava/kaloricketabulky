"""Parse Czech-localized number strings (thin-space thousands, decimal comma)."""

# Thousands separators the API emits: space, no-break, thin, narrow no-break.
_THOUSANDS_SEPARATORS = (" ", "\u00a0", "\u2009", "\u202f")


def parse_czech_number(raw: str | None) -> float | None:
    """Parse a Czech-localized number string into a float.

    Handles thin/non-breaking/regular-space thousands separators and the decimal
    comma. Returns None for None/blank input. Raises ValueError for non-numeric text.
    """
    if raw is None:
        return None
    cleaned = raw.strip()
    if not cleaned:
        return None
    for separator in _THOUSANDS_SEPARATORS:
        cleaned = cleaned.replace(separator, "")
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"not a number: {raw!r}") from exc
