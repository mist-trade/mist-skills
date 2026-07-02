from typing import cast

from shared.api_contracts import API_ENDPOINTS
from shared.mist_client import MistClient
from shared.script_runner import run_cli


def main() -> list:
    client = MistClient()
    return cast(list, client.get(API_ENDPOINTS.security_all))


if __name__ == "__main__":
    run_cli(main)
