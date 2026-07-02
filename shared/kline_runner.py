import sys
from collections.abc import Collection
from typing import Any

from shared.config import get_default_source
from shared.mist_client import MistApiError, MistClient
from shared.periods import PeriodInput, normalize_period
from shared.securities import source_format_code, split_exchange_suffix


INTRADAY_PERIODS = frozenset({1, 5, 15, 30, 60})
DAILY_PERIOD = 1440


def run_kline_query(
    *,
    client: MistClient,
    code: str,
    period: PeriodInput,
    start_date: str,
    end_date: str,
    source: str | None = None,
    name: str | None = None,
    auto_collect: bool = True,
    allowed_periods: Collection[int] | None = None,
    invalid_period_message: str | None = None,
) -> list:
    normalized_period = normalize_period(period)
    if allowed_periods is not None and normalized_period not in allowed_periods:
        print(
            invalid_period_message
            or f"Error: unsupported period {normalized_period}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    effective_source = source or get_default_source()
    try:
        result = query_kline(
            client,
            code,
            normalized_period,
            start_date,
            end_date,
            effective_source,
        )
    except MistApiError as exc:
        if not auto_collect or not should_collect_after_error(exc):
            raise
    else:
        if result or not auto_collect:
            return result

    backend_code, _ = split_exchange_suffix(code)
    ensure_security(client, backend_code, code, effective_source, name)
    collect_kline(
        client,
        backend_code,
        normalized_period,
        start_date,
        end_date,
        effective_source,
    )
    return query_kline(
        client,
        backend_code,
        normalized_period,
        start_date,
        end_date,
        effective_source,
    )


def query_kline(
    client: MistClient,
    code: str,
    period: int,
    start_date: str,
    end_date: str,
    source: str,
) -> list:
    return client.post(
        "/indicator/k",
        {
            "code": code,
            "period": period,
            "startDate": start_date,
            "endDate": end_date,
            "source": source,
        },
    )


def should_collect_after_error(error: MistApiError) -> bool:
    message = str(error)
    return (
        "Index information not found" in message
        or "Security with code" in message
        or error.error_code in {400, 404}
    )


def ensure_security(
    client: MistClient,
    backend_code: str,
    requested_code: str,
    source: str,
    name: str | None = None,
) -> None:
    try:
        client.get(f"/security/v1/{backend_code}")
    except MistApiError:
        client.post(
            "/security/v1/initialize",
            {
                "code": backend_code,
                "name": name or backend_code,
                "type": "STOCK",
            },
        )

    client.post(
        "/security/v1/sources",
        {
            "code": backend_code,
            "source": source,
            "formatCode": source_format_code(requested_code),
            "priority": 100,
            "enabled": True,
        },
    )


def collect_kline(
    client: MistClient,
    backend_code: str,
    period: int,
    start_date: str,
    end_date: str,
    source: str,
) -> dict[str, Any] | list:
    return client.post(
        "/v1/collector/collect",
        {
            "code": backend_code,
            "period": period,
            "startDate": start_date,
            "endDate": end_date,
            "source": source,
        },
    )
