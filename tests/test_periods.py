import pytest

from shared.periods import normalize_period


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1min", 1),
        ("5min", 5),
        ("15min", 15),
        ("30min", 30),
        ("60min", 60),
        ("daily", 1440),
        ("day", 1440),
        ("1440", 1440),
        (1440, 1440),
    ],
)
def test_normalize_period_accepts_skill_aliases(value, expected):
    assert normalize_period(value) == expected


def test_normalize_period_rejects_unknown_values():
    with pytest.raises(ValueError, match="Unsupported period"):
        normalize_period("2min")
