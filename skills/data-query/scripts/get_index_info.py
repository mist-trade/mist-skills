import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient
from shared.script_runner import run_cli
from shared.securities import split_exchange_suffix


def main(code: str) -> dict:
    client = MistClient()
    backend_code, _ = split_exchange_suffix(code)
    return client.get(f"/security/v1/{backend_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get security details by code")
    parser.add_argument("--code", required=True, help="Security code (e.g., 000001.SH)")
    args = parser.parse_args()
    run_cli(lambda: main(args.code))
