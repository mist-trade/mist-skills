import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient


def main(code: str, start_date: str, end_date: str,
         source: str | None = None) -> list:
    body = {"code": code, "period": "daily", "startDate": start_date, "endDate": end_date}
    if source:
        body["source"] = source

    client = MistClient()
    return client.post("/indicator/k", body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get daily K-line data")
    parser.add_argument("--code", required=True, help="Security code")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", help="Data source (ef/tdx/mqmt)")
    args = parser.parse_args()
    result = main(args.code, args.start_date, args.end_date, args.source)
    print(json.dumps(result, ensure_ascii=False))
