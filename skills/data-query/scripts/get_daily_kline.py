import argparse

from shared.api_contracts import SOURCE_HELP_TEXT
from shared.kline_runner import DAILY_PERIOD, run_kline_query
from shared.mist_client import MistClient
from shared.script_runner import run_cli


def main(
    code: str,
    start_date: str,
    end_date: str,
    source: str | None = None,
    name: str | None = None,
    auto_collect: bool = True,
) -> list:
    return run_kline_query(
        client=MistClient(),
        code=code,
        period=DAILY_PERIOD,
        start_date=start_date,
        end_date=end_date,
        source=source,
        name=name,
        auto_collect=auto_collect,
        allowed_periods={DAILY_PERIOD},
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get daily K-line data")
    parser.add_argument("--code", required=True, help="Security code")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", help=SOURCE_HELP_TEXT)
    parser.add_argument("--name", help="Security display name for first-time initialization")
    parser.add_argument("--no-auto-collect", action="store_true", help="Only query stored data")
    args = parser.parse_args()
    run_cli(
        lambda: main(
            args.code,
            args.start_date,
            args.end_date,
            args.source,
            args.name,
            not args.no_auto_collect,
        )
    )
