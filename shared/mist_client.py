from typing import Any, TypeAlias

import requests

from shared.config import get_base_url, get_timeout

JsonObject: TypeAlias = dict[str, Any]
JsonArray: TypeAlias = list[Any]
MistPayload: TypeAlias = JsonObject | JsonArray


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

    def get_object(self, path: str) -> JsonObject:
        return self._expect_object(self._get_payload(path))

    def get_list(self, path: str) -> JsonArray:
        return self._expect_list(self._get_payload(path))

    def post_object(self, path: str, body: JsonObject) -> JsonObject:
        return self._expect_object(self._post_payload(path, body))

    def post_list(self, path: str, body: JsonObject) -> JsonArray:
        return self._expect_list(self._post_payload(path, body))

    def _get_payload(self, path: str) -> MistPayload:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as e:
            raise MistConnectionError(f"Cannot connect to mist backend: {e}") from e
        return self._parse_response(resp)

    def _post_payload(self, path: str, body: JsonObject) -> MistPayload:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.post(url, json=body, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as e:
            raise MistConnectionError(f"Cannot connect to mist backend: {e}") from e
        return self._parse_response(resp)

    def _parse_response(self, resp: requests.Response) -> MistPayload:
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

    def _expect_object(self, payload: MistPayload) -> JsonObject:
        if not isinstance(payload, dict):
            raise MistApiError("Malformed success response: data is not an object", 0)
        return payload

    def _expect_list(self, payload: MistPayload) -> JsonArray:
        if not isinstance(payload, list):
            raise MistApiError("Malformed success response: data is not a list", 0)
        return payload
