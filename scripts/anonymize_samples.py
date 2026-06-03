"""Build anonymized test fixtures from sample-responses/.

The fixtures keep the *structure* of real API responses (so the models and their
edge cases stay exercised) while destroying the real *values*. The transform is
deliberately NOT invertible from this repository: numbers are replaced with fresh
random values drawn independently of the originals -- never a fixed scaling of
them -- so neither the committed fixtures nor this script reveal anything about the
source data (not the exact value, not even its magnitude).

Per sample:
- remap each 32-hex GUID to a deterministic fake derived from first-seen order;
- replace every number with an independent random value of the same kind -- counts
  and codes with a small integer, measurements with a small float, millisecond
  timestamps with a random instant in 2020 -- including numbers encoded as strings
  (food energy, localized "2 384"/"85,2"); the envelope `code` is preserved so the
  responses still read as successful;
- null the redundant display strings `valueString` and `description`;
- replace the `date`/`weekDate` display strings with fixed fake dates (kept in
  DD.MM.YYYY form so the models still parse them);
- genericize the `title` and `url` of foodstuff/activity entries to neutral
  placeholders (e.g. "Foodstuff 1", "foodstuff-1");
- keep structure, keys, units of measure, meal names, macro names, tip text, and
  codes intact.

Re-running regenerates different (still anonymous) values; the committed fixtures
were generated once. Run: uv run python scripts/anonymize_samples.py
"""

import json
import re
from pathlib import Path
from random import SystemRandom

SOURCE = Path("sample-responses")
DEST = Path("tests/fixtures")
GUID_RE = re.compile(r"\b[0-9a-f]{32}\b")
NUMERIC_STRING_RE = re.compile(r"-?[\d.,]+")
# Thousands separators the API emits: space, no-break, thin, narrow no-break.
_SPACES = (" ", "\u00a0", "\u2009", "\u202f")  # space, no-break, thin, narrow no-break
_NULLED_KEYS = frozenset({"valueString", "description"})
_PRESERVED_NUMERIC_KEYS = frozenset({"code"})
_LABELLED_TYPES = frozenset({"foodstuff", "activity"})
_FAKE_DATE = "01.01.2020"
_FAKE_DATE_RANGE = "01.01.2020 - 07.01.2020"

# Values at or above this are millisecond timestamps; anonymize them to a 2020 instant.
_EPOCH_THRESHOLD = 10**12
_EPOCH_MIN = 1577836800000  # 2020-01-01T00:00:00Z
_EPOCH_MAX = 1609372800000  # 2020-12-31T00:00:00Z

_rng = SystemRandom()
_guid_map: dict[str, str] = {}
_label_indices: dict[tuple[str, str], int] = {}
_label_counters: dict[str, int] = {}


def _fake_guid(match: re.Match[str]) -> str:
    original = match.group(0)
    if original not in _guid_map:
        _guid_map[original] = f"{len(_guid_map):032x}"
    return _guid_map[original]


def _label_index(item_type: str, title: object) -> int:
    """Return a stable 1-based index per unique (type, title), shared by title and url."""
    identity = (item_type, title if isinstance(title, str) else "")
    if identity not in _label_indices:
        _label_counters[item_type] = _label_counters.get(item_type, 0) + 1
        _label_indices[identity] = _label_counters[item_type]
    return _label_indices[identity]


def _fake_number(value: int | float) -> int | float:
    if isinstance(value, int):
        if abs(value) >= _EPOCH_THRESHOLD:
            return _rng.randint(_EPOCH_MIN, _EPOCH_MAX)
        return _rng.randint(0, 100)
    return round(_rng.uniform(0, 100), 3)


def _fake_numeric_string(text: str) -> str | None:
    cleaned = text
    for separator in _SPACES:
        cleaned = cleaned.replace(separator, "")
    if not NUMERIC_STRING_RE.fullmatch(cleaned) or not any(char.isdigit() for char in cleaned):
        return None
    had_comma = "," in cleaned and "." not in cleaned
    rendered = f"{round(_rng.uniform(0, 100), 3):g}"
    return rendered.replace(".", ",") if had_comma else rendered


def _scrub(value: object, key: str | None = None) -> object:
    if key in _NULLED_KEYS:
        return None
    if key in _PRESERVED_NUMERIC_KEYS and isinstance(value, int) and not isinstance(value, bool):
        return value
    if key == "date" and isinstance(value, str):
        return _FAKE_DATE
    if key == "weekDate" and isinstance(value, str):
        return _FAKE_DATE_RANGE
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return _fake_number(value)
    if isinstance(value, str):
        if GUID_RE.search(value):
            return GUID_RE.sub(_fake_guid, value)
        faked = _fake_numeric_string(value)
        return faked if faked is not None else value
    if isinstance(value, list):
        return [_scrub(item) for item in value]
    if isinstance(value, dict):
        item_type = value.get("type")
        if item_type in _LABELLED_TYPES:
            index = _label_index(item_type, value.get("title"))
            return {
                sub_key: _labelled_field(item_type, index, sub_key, sub_value) for sub_key, sub_value in value.items()
            }
        return {sub_key: _scrub(sub_value, sub_key) for sub_key, sub_value in value.items()}
    return value


def _labelled_field(item_type: str, index: int, key: str, value: object) -> object:
    """Replace the title/url of a foodstuff/activity with neutral placeholders."""
    if key == "title" and isinstance(value, str):
        return f"{item_type.capitalize()} {index}"
    if key == "url" and isinstance(value, str):
        return f"{item_type}-{index}"
    return _scrub(value, key)


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for path in sorted(SOURCE.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        scrubbed = _scrub(raw)
        (DEST / path.name).write_text(json.dumps(scrubbed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {DEST / path.name}")  # noqa: T201 - script progress output


if __name__ == "__main__":
    main()
