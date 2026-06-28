import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.config import get_default_source
from shared.mist_client import MistApiError, MistClient
from shared.periods import normalize_period
from shared.securities import source_format_code, split_exchange_suffix


def main(code: str, start_date: str, end_date: str,
         source: str | None = None, name: str | None = None,
         auto_collect: bool = True) -> list:
    effective_source = source or get_default_source()
    client = MistClient()
    try:
        result = query_daily_kline(client, code, start_date, end_date, effective_source)
    except MistApiError as exc:
        if not auto_collect or not should_collect_after_error(exc):
            raise
    else:
        if result or not auto_collect:
            return result

    backend_code, _ = split_exchange_suffix(code)
    ensure_security(client, backend_code, code, effective_source, name)
    collect_daily_kline(client, backend_code, start_date, end_date, effective_source)
    return query_daily_kline(client, backend_code, start_date, end_date, effective_source)


def query_daily_kline(client: MistClient, code: str, start_date: str,
                      end_date: str, source: str) -> list:
    body = {
        "code": code,
        "period": normalize_period("daily"),
        "startDate": start_date,
        "endDate": end_date,
        "source": source,
    }
    return client.post("/indicator/k", body)


def should_collect_after_error(error: MistApiError) -> bool:
    message = str(error)
    return (
        "Index information not found" in message
        or "Security with code" in message
        or error.error_code in {400, 404}
    )


def ensure_security(client: MistClient, backend_code: str, requested_code: str,
                    source: str, name: str | None = None) -> None:
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


def collect_daily_kline(client: MistClient, backend_code: str, start_date: str,
                        end_date: str, source: str) -> dict | list:
    return client.post(
        "/v1/collector/collect",
        {
            "code": backend_code,
            "period": normalize_period("daily"),
            "startDate": start_date,
            "endDate": end_date,
            "source": source,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get daily K-line data")
    parser.add_argument("--code", required=True, help="Security code")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", help="Data source (ef/tdx/mqmt)")
    parser.add_argument("--name", help="Security display name for first-time initialization")
    parser.add_argument("--no-auto-collect", action="store_true", help="Only query stored data")
    args = parser.parse_args()
    result = main(
        args.code,
        args.start_date,
        args.end_date,
        args.source,
        args.name,
        not args.no_auto_collect,
    )
    print(json.dumps(result, ensure_ascii=False))
