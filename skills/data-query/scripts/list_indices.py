import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.mist_client import MistClient
from shared.script_runner import run_cli


def main() -> list:
    client = MistClient()
    return client.get("/security/v1/all")


if __name__ == "__main__":
    run_cli(main)
