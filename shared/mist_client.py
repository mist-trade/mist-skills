import requests

from shared.config import get_base_url, get_timeout


class MistConnectionError(Exception):
    """Raised when unable to connect to mist backend."""

    pass


class MistApiError(Exception):
    """Raised when mist backend returns a business error."""

    def __init__(self, message: str, error_code: int):
        super().__init__(message)
        self.error_code = error_code


class MistClient:
    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.timeout = timeout or get_timeout()

    def get(self, path: str) -> dict | list:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as e:
            raise MistConnectionError(f"Cannot connect to mist backend: {e}") from e
        return self._parse_response(resp)

    def post(self, path: str, body: dict) -> dict | list:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.post(url, json=body, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as e:
            raise MistConnectionError(f"Cannot connect to mist backend: {e}") from e
        return self._parse_response(resp)

    def _parse_response(self, resp: requests.Response) -> dict | list:
        data = resp.json()
        if not data.get("success", False):
            raise MistApiError(
                message=data.get("message", "Unknown error"),
                error_code=data.get("statusCode", 0),
            )
        if "data" not in data:
            raise MistApiError(
                message="Malformed success response: missing data",
                error_code=data.get("statusCode", resp.status_code),
            )
        return data["data"]
