import json
import sys
from collections.abc import Callable
from typing import Any

from shared.mist_client import MistApiError, MistClient, MistConnectionError
from shared.periods import PeriodInput, normalize_period
from shared.securities import split_exchange_suffix


def build_analysis_body(
    *,
    code: str,
    period: PeriodInput,
    start_date: str,
    end_date: str,
    source: str | None = None,
) -> dict[str, Any]:
    backend_code, _ = split_exchange_suffix(code)
    body: dict[str, Any] = {
        "code": backend_code,
        "period": normalize_period(period),
        "startDate": start_date,
        "endDate": end_date,
    }
    if source:
        body["source"] = source
    return body


def run_simple_post(
    *,
    endpoint: str,
    code: str,
    period: PeriodInput,
    start_date: str,
    end_date: str,
    source: str | None = None,
    client: MistClient | None = None,
) -> dict | list:
    active_client = client or MistClient()
    return active_client.post(
        endpoint,
        build_analysis_body(
            code=code,
            period=period,
            start_date=start_date,
            end_date=end_date,
            source=source,
        ),
    )


def print_json(result: Any) -> None:
    print(json.dumps(result, ensure_ascii=False))


def run_cli(action: Callable[[], Any]) -> None:
    try:
        print_json(action())
    except MistConnectionError as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except MistApiError as exc:
        print(f"Mist API error ({exc.error_code}): {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
