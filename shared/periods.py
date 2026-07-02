PeriodInput = int | str


PERIOD_ALIASES: dict[str, int] = {
    "1": 1,
    "1m": 1,
    "1min": 1,
    "5": 5,
    "5m": 5,
    "5min": 5,
    "15": 15,
    "15m": 15,
    "15min": 15,
    "30": 30,
    "30m": 30,
    "30min": 30,
    "60": 60,
    "60m": 60,
    "60min": 60,
    "1440": 1440,
    "day": 1440,
    "daily": 1440,
}


def normalize_period(period: PeriodInput) -> int:
    if isinstance(period, int):
        if period in PERIOD_ALIASES.values():
            return period
        raise ValueError(f"Unsupported period: {period}")

    normalized = period.strip().lower()
    try:
        return PERIOD_ALIASES[normalized]
    except KeyError as exc:
        supported = ", ".join(sorted(PERIOD_ALIASES))
        raise ValueError(f"Unsupported period: {period}. Supported values: {supported}") from exc
