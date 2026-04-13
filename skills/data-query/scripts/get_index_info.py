import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient


def main(code: str) -> dict:
    client = MistClient()
    return client.get(f"/security/v1/{code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get security details by code")
    parser.add_argument("--code", required=True, help="Security code (e.g., 000001.SH)")
    args = parser.parse_args()
    result = main(args.code)
    print(json.dumps(result, ensure_ascii=False))
