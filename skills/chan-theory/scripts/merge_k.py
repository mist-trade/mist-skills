import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient
from shared.periods import normalize_period
from shared.securities import split_exchange_suffix


def main(code: str, period: str, start_date: str, end_date: str,
         source: str | None = None) -> list:
    backend_code, _ = split_exchange_suffix(code)
    body = {"code": backend_code, "period": normalize_period(period), "startDate": start_date, "endDate": end_date}
    if source:
        body["source"] = source

    client = MistClient()
    return client.post("/chan/merge-k", body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge K-lines by containment")
    parser.add_argument("--code", required=True, help="Security code")
    parser.add_argument("--period", required=True, help="Period (1min/5min/15min/30min/60min/daily)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", help="Data source (ef/tdx/mqmt)")
    args = parser.parse_args()
    result = main(args.code, args.period, args.start_date, args.end_date, args.source)
    print(json.dumps(result, ensure_ascii=False))
