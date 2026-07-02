import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient
from shared.script_runner import run_cli


def main(code: str) -> dict:
    client = MistClient()
    return client.get(f"/security/v1/{code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get security details by code")
    parser.add_argument("--code", required=True, help="Security code (e.g., 000001.SH)")
    args = parser.parse_args()
    run_cli(lambda: main(args.code))
