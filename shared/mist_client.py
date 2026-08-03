from typing import Any, TypeAlias

import requests

from shared.config import get_base_url, get_timeout

JsonObject: TypeAlias = dict[str, Any]
JsonArray: TypeAlias = list[Any]

#: HTTP response header carrying the server-generated request id.
REQUEST_ID_HEADER = "x-request-id"


class MistConnectionError(Exception):
    """Raised when unable to connect to mist backend (connection/timeout only)."""

    pass


class MistApiError(Exception):
    """Raised when the backend returns a valid error envelope.

    Covers both an HTTP-200 expected business rejection and a real non-2xx
    technical failure. ``code`` is the stable machine-readable identifier;
    ``http_status`` mirrors the real HTTP status for diagnostics only and MUST
    NOT drive business logic.
    """

    code: str
    http_status: int
    request_id: str | None
    data: Any
    errors: dict[str, list[str]] | None

    def __init__(
        self,
        message: str,
        code: str,
        http_status: int,
        *,
        request_id: str | None = None,
        data: Any = None,
        errors: dict[str, list[str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.request_id = request_id
        self.data = data
        self.errors = errors


class MistApiContractError(Exception):
    """Raised when the response cannot be interpreted as the unified envelope.

    Covers non-JSON bodies, bare business payloads, missing/typed-wrong
    required fields, an error/success branch mismatch and a body ``statusCode``
    that disagrees with the real HTTP status. This is a consumer/contract
    failure, never a server-declared API error, so it carries no ``code``.
    """

    http_status: int
    request_id: str | None

    def __init__(self, message: str, *, http_status: int, request_id: str | None = None) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.request_id = request_id


def _envelope_request_id(resp: requests.Response) -> str | None:
    value = resp.headers.get(REQUEST_ID_HEADER)
    return value if value else None


def _require_field(
    body: dict[str, Any],
    field: str,
    *,
    http_status: int,
    request_id: str | None,
) -> Any:
    if field not in body:
        raise MistApiContractError(
            f'Envelope field "{field}" is missing',
            http_status=http_status,
            request_id=request_id,
        )
    return body[field]


def _require_str_field(
    body: dict[str, Any],
    field: str,
    *,
    http_status: int,
    request_id: str | None,
) -> str:
    value = _require_field(body, field, http_status=http_status, request_id=request_id)
    if not isinstance(value, str) or not value:
        raise MistApiContractError(
            f'Envelope field "{field}" must be a non-empty string',
            http_status=http_status,
            request_id=request_id,
        )
    return value


def _is_successful_http_status(status: int) -> bool:
    return 200 <= status < 300


def _parse_errors_field(
    value: Any,
    *,
    http_status: int,
    request_id: str,
) -> dict[str, list[str]]:
    if not isinstance(value, dict) or not all(
        isinstance(key, str)
        and isinstance(messages, list)
        and all(isinstance(message, str) for message in messages)
        for key, messages in value.items()
    ):
        raise MistApiContractError(
            'Envelope field "errors" must be an object of string arrays',
            http_status=http_status,
            request_id=request_id,
        )
    return value


def parse_envelope(body: Any, http_status: int, request_id: str | None) -> Any:
    """Strictly parse a non-204 JSON body against the unified backend envelope.

    Validates every required known field and the success/error branch, asserts
    that body ``statusCode`` equals the real HTTP status, and rejects bare
    payloads, malformed envelopes and status mismatches with
    :class:`MistApiContractError`. Additive unknown fields are tolerated for
    forward compatibility, but a known field with the wrong type still fails
    closed.

    A valid success branch returns its ``data``; a valid error branch
    (HTTP-200 business rejection or a real non-2xx technical failure) raises
    :class:`MistApiError`.
    """
    if not isinstance(body, dict):
        raise MistApiContractError(
            "Response body is not a JSON object envelope",
            http_status=http_status,
            request_id=request_id,
        )

    success = _require_field(body, "success", http_status=http_status, request_id=request_id)
    if not isinstance(success, bool):
        raise MistApiContractError(
            'Envelope field "success" must be a boolean',
            http_status=http_status,
            request_id=request_id,
        )

    body_status = _require_field(body, "statusCode", http_status=http_status, request_id=request_id)
    if not isinstance(body_status, int) or isinstance(body_status, bool):
        raise MistApiContractError(
            'Envelope field "statusCode" must be a number',
            http_status=http_status,
            request_id=request_id,
        )
    if body_status != http_status:
        raise MistApiContractError(
            f"Envelope statusCode {body_status} does not match HTTP status {http_status}",
            http_status=http_status,
            request_id=request_id,
        )

    message = _require_str_field(body, "message", http_status=http_status, request_id=request_id)
    envelope_request_id = _require_str_field(
        body, "requestId", http_status=http_status, request_id=request_id
    )
    _require_str_field(body, "timestamp", http_status=http_status, request_id=request_id)
    _require_str_field(body, "path", http_status=http_status, request_id=request_id)

    successful_http_status = _is_successful_http_status(http_status)
    if success and not successful_http_status:
        raise MistApiContractError(
            f"A non-2xx HTTP response cannot declare success=true (HTTP {http_status})",
            http_status=http_status,
            request_id=envelope_request_id,
        )
    if not success and successful_http_status and http_status != 200:
        raise MistApiContractError(
            f"Only HTTP 200 may carry an expected business rejection (HTTP {http_status})",
            http_status=http_status,
            request_id=envelope_request_id,
        )

    if success:
        # A non-204 success envelope must carry the documented `data` slot; it may
        # legitimately be None when the controller returns no business data.
        # Additive unknown fields are ignored.
        if "data" not in body:
            raise MistApiContractError(
                'Success envelope is missing the "data" field',
                http_status=http_status,
                request_id=request_id,
            )
        return body["data"]

    code = _require_str_field(body, "code", http_status=http_status, request_id=request_id)
    errors: dict[str, list[str]] | None
    if "errors" not in body:
        errors = None
    else:
        if http_status != 400 or code != "VALIDATION_ERROR":
            raise MistApiContractError(
                'Envelope field "errors" is only valid for HTTP 400 VALIDATION_ERROR',
                http_status=http_status,
                request_id=envelope_request_id,
            )
        errors = _parse_errors_field(
            body["errors"],
            http_status=http_status,
            request_id=envelope_request_id,
        )

    raise MistApiError(
        message,
        code,
        http_status,
        request_id=envelope_request_id,
        data=body.get("data"),
        errors=errors,
    )


class MistClient:
    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.timeout = timeout or get_timeout()

    def get_object(self, path: str) -> JsonObject:
        payload, http_status, request_id = self._request_payload("GET", path, None)
        return self._expect_object(
            payload,
            http_status=http_status,
            request_id=request_id,
        )

    def get_list(self, path: str) -> JsonArray:
        payload, http_status, request_id = self._request_payload("GET", path, None)
        return self._expect_list(
            payload,
            http_status=http_status,
            request_id=request_id,
        )

    def post_object(self, path: str, body: JsonObject) -> JsonObject:
        payload, http_status, request_id = self._request_payload("POST", path, body)
        return self._expect_object(
            payload,
            http_status=http_status,
            request_id=request_id,
        )

    def post_list(self, path: str, body: JsonObject) -> JsonArray:
        payload, http_status, request_id = self._request_payload("POST", path, body)
        return self._expect_list(
            payload,
            http_status=http_status,
            request_id=request_id,
        )

    def request_no_content(
        self, method: str, path: str, body: JsonObject | None = None
    ) -> str | None:
        """Perform a request declared to return no content.

        Only an HTTP 204 with an empty body is accepted; it never attempts to
        parse JSON. Returns the server-generated ``X-Request-Id`` response
        header (if present) for diagnostics. Any other status fails closed.
        """
        resp = self._send(method, path, body)
        request_id = _envelope_request_id(resp)
        if resp.status_code != 204:
            raise MistApiContractError(
                f"Expected HTTP 204 No Content but received status {resp.status_code}",
                http_status=resp.status_code,
                request_id=request_id,
            )
        return request_id

    def _request_payload(
        self,
        method: str,
        path: str,
        body: JsonObject | None,
    ) -> tuple[Any, int, str | None]:
        resp = self._send(method, path, body)
        request_id = _envelope_request_id(resp)
        return self._parse_response(resp), resp.status_code, request_id

    def _send(self, method: str, path: str, body: JsonObject | None) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            if method == "GET":
                return requests.get(url, timeout=self.timeout)
            if method == "POST":
                return requests.post(url, json=body, timeout=self.timeout)
            return requests.request(method, url, json=body, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as e:
            raise MistConnectionError(f"Cannot connect to mist backend: {e}") from e

    def _parse_response(self, resp: requests.Response) -> Any:
        request_id = _envelope_request_id(resp)
        try:
            body = resp.json()
        except ValueError as e:
            raise MistApiContractError(
                f"Response body is not valid JSON (HTTP {resp.status_code})",
                http_status=resp.status_code,
                request_id=request_id,
            ) from e
        return parse_envelope(body, resp.status_code, request_id)

    def _expect_object(
        self,
        payload: Any,
        *,
        http_status: int,
        request_id: str | None,
    ) -> JsonObject:
        if not isinstance(payload, dict):
            raise MistApiContractError(
                "Success response data is not an object",
                http_status=http_status,
                request_id=request_id,
            )
        return payload

    def _expect_list(
        self,
        payload: Any,
        *,
        http_status: int,
        request_id: str | None,
    ) -> JsonArray:
        if not isinstance(payload, list):
            raise MistApiContractError(
                "Success response data is not a list",
                http_status=http_status,
                request_id=request_id,
            )
        return payload
