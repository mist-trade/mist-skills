import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient
from shared.script_runner import run_cli, run_simple_post


def main(code: str, period: str, start_date: str, end_date: str,
         source: str | None = None) -> list:
    return run_simple_post(
        endpoint="/indicator/rsi",
        code=code,
        period=period,
        start_date=start_date,
        end_date=end_date,
        source=source,
        client=MistClient(),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate RSI indicator")
    parser.add_argument("--code", required=True, help="Security code")
    parser.add_argument("--period", required=True, help="Period (1min/5min/15min/30min/60min/daily)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", help="Data source (ef/tdx/mqmt)")
    args = parser.parse_args()
    run_cli(lambda: main(args.code, args.period, args.start_date, args.end_date, args.source))
