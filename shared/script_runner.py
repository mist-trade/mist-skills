import json
import sys
from collections.abc import Callable
from typing import Any, cast

from shared.api_contracts import (
    FIELD_CODE,
    FIELD_END_DATE,
    FIELD_PERIOD,
    FIELD_SOURCE,
    FIELD_START_DATE,
)
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
        FIELD_CODE: backend_code,
        FIELD_PERIOD: normalize_period(period),
        FIELD_START_DATE: start_date,
        FIELD_END_DATE: end_date,
    }
    if source:
        body[FIELD_SOURCE] = source
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
) -> list:
    active_client = client or MistClient()
    return cast(
        list,
        active_client.post(
            endpoint,
            build_analysis_body(
                code=code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                source=source,
            ),
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
