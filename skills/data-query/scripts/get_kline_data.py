import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.kline_runner import INTRADAY_PERIODS, run_kline_query
from shared.mist_client import MistClient
from shared.script_runner import run_cli


def main(code: str, period: str, start_date: str, end_date: str,
         source: str | None = None, name: str | None = None,
         auto_collect: bool = True) -> list:
    return run_kline_query(
        client=MistClient(),
        code=code,
        period=period,
        start_date=start_date,
        end_date=end_date,
        source=source,
        name=name,
        auto_collect=auto_collect,
        allowed_periods=INTRADAY_PERIODS,
        invalid_period_message="Error: period must be one of 1min, 5min, 15min, 30min, 60min",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get intraday K-line data")
    parser.add_argument("--code", required=True, help="Security code")
    parser.add_argument("--period", required=True, help="Period (1min/5min/15min/30min/60min)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", help="Data source (ef/tdx/mqmt)")
    parser.add_argument("--name", help="Security display name for first-time initialization")
    parser.add_argument("--no-auto-collect", action="store_true", help="Only query stored data")
    args = parser.parse_args()
    run_cli(
        lambda: main(
            args.code,
            args.period,
            args.start_date,
            args.end_date,
            args.source,
            args.name,
            not args.no_auto_collect,
        )
    )
