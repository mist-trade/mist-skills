from unittest.mock import MagicMock, patch

import pytest

from shared.mist_client import (
    MistApiContractError,
    MistApiError,
    MistClient,
    MistConnectionError,
    parse_envelope,
)


def _resp(body, status=200, *, request_id="http-1", json_error=None):
    resp = MagicMock()
    resp.status_code = status
    if json_error is not None:
        resp.json.side_effect = json_error
    else:
        resp.json.return_value = body
    headers = {}
    if request_id is not None:
        headers["x-request-id"] = request_id
    resp.headers.get.side_effect = lambda key, default=None: headers.get(key, default)
    return resp


def success_envelope(data, *, status=200, request_id="http-success-1", path="/v1/securities"):
    return _resp(
        {
            "success": True,
            "statusCode": status,
            "message": "SUCCESS",
            "data": data,
            "timestamp": "2026-08-03T00:00:00.000Z",
            "requestId": request_id,
            "path": path,
        },
        status=status,
        request_id=request_id,
    )


def error_envelope(
    status,
    code,
    message,
    *,
    request_id=None,
    data=None,
    errors=None,
    body_status=None,
):
    rid = request_id or f"http-{code.lower()}"
    return _resp(
        {
            "success": False,
            "statusCode": body_status if body_status is not None else status,
            "code": code,
            "message": message,
            "data": data,
            "errors": errors,
            "timestamp": "2026-08-03T00:00:00.000Z",
            "requestId": rid,
            "path": "/v1/securities",
        },
        status=status,
        request_id=rid,
    )


@pytest.fixture
def client():
    return MistClient()


@pytest.fixture
def success_response():
    return success_envelope({"key": "value"})


# ---------------------------------------------------------------------------
# parse_envelope contract (mirrors the mist-fe parser semantics)
# ---------------------------------------------------------------------------


class TestParseEnvelope:
    def test_returns_typed_data_from_http_200_success_envelope(self):
        data = parse_envelope(
            {
                "success": True,
                "statusCode": 200,
                "message": "SUCCESS",
                "data": [{"code": "600519"}],
                "timestamp": "2026-08-03T00:00:00.000Z",
                "requestId": "http-1",
                "path": "/v1/securities",
            },
            200,
            None,
        )
        assert data == [{"code": "600519"}]

    def test_returns_data_from_http_201_success_envelope(self):
        data = parse_envelope(
            {
                "success": True,
                "statusCode": 201,
                "message": "CREATED",
                "data": {"id": 7},
                "timestamp": "2026-08-03T00:00:00.000Z",
                "requestId": "http-2",
                "path": "/v1/strategies",
            },
            201,
            None,
        )
        assert data == {"id": 7}

    def test_raises_mist_api_error_for_http_200_business_rejection(self):
        with pytest.raises(MistApiError):
            parse_envelope(
                {
                    "success": False,
                    "statusCode": 200,
                    "code": "BACKTEST_QUEUE_FULL",
                    "message": "queue full",
                    "data": {"capacity": 100},
                    "timestamp": "2026-08-03T00:00:00.000Z",
                    "requestId": "http-biz",
                    "path": "/v1/strategy-backtests",
                },
                200,
                None,
            )

    @pytest.mark.parametrize(
        "status,code",
        [(400, "BAD_REQUEST"), (500, "INTERNAL_ERROR"), (502, "BAD_GATEWAY")],
    )
    def test_raises_mist_api_error_for_non_2xx_technical_error(self, status, code):
        with pytest.raises(MistApiError):
            parse_envelope(
                {
                    "success": False,
                    "statusCode": status,
                    "code": code,
                    "message": "fail",
                    "timestamp": "2026-08-03T00:00:00.000Z",
                    "requestId": f"http-{status}",
                    "path": "/v1/securities",
                },
                status,
                None,
            )

    def test_rejects_bare_array_payload_as_contract_error(self):
        with pytest.raises(MistApiContractError):
            parse_envelope([{"code": "000001"}], 200, None)

    def test_rejects_bare_primitive_payload_as_contract_error(self):
        with pytest.raises(MistApiContractError):
            parse_envelope(42, 200, None)

    def test_rejects_non_object_body(self):
        with pytest.raises(MistApiContractError):
            parse_envelope("not an object", 200, None)

    def test_rejects_missing_required_field(self):
        with pytest.raises(MistApiContractError):
            parse_envelope(
                {
                    "success": True,
                    "statusCode": 200,
                    "message": "SUCCESS",
                    "data": None,
                    # timestamp missing
                    "requestId": "http-1",
                    "path": "/v1/securities",
                },
                200,
                None,
            )

    def test_rejects_known_field_with_wrong_type(self):
        with pytest.raises(MistApiContractError):
            parse_envelope(
                {
                    "success": "true",
                    "statusCode": 200,
                    "message": "SUCCESS",
                    "data": None,
                    "timestamp": "2026-08-03T00:00:00.000Z",
                    "requestId": "http-1",
                    "path": "/v1/securities",
                },
                200,
                None,
            )

    def test_rejects_status_mismatch(self):
        with pytest.raises(MistApiContractError):
            parse_envelope(
                {
                    "success": False,
                    "statusCode": 404,
                    "code": "NOT_FOUND",
                    "message": "missing",
                    "timestamp": "2026-08-03T00:00:00.000Z",
                    "requestId": "http-1",
                    "path": "/v1/securities",
                },
                200,
                None,
            )

    def test_tolerates_additive_unknown_fields(self):
        data = parse_envelope(
            {
                "success": True,
                "statusCode": 200,
                "message": "SUCCESS",
                "data": {"code": "600519"},
                "timestamp": "2026-08-03T00:00:00.000Z",
                "requestId": "http-1",
                "path": "/v1/securities",
                "traceId": "trace-xyz",
                "serverVersion": "1.2.3",
            },
            200,
            None,
        )
        assert data == {"code": "600519"}

    def test_preserves_error_fields_on_thrown_api_error(self):
        with pytest.raises(MistApiError) as exc_info:
            parse_envelope(
                {
                    "success": False,
                    "statusCode": 400,
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "data": {"field": "code"},
                    "errors": {"code": ["must not be empty"]},
                    "timestamp": "2026-08-03T00:00:00.000Z",
                    "requestId": "http-val",
                    "path": "/v1/securities",
                },
                400,
                None,
            )
        err = exc_info.value
        assert err.code == "VALIDATION_ERROR"
        assert err.http_status == 400
        assert err.request_id == "http-val"
        assert err.errors == {"code": ["must not be empty"]}
        assert str(err) == "Request validation failed"


# ---------------------------------------------------------------------------
# MistClient request behavior
# ---------------------------------------------------------------------------


class TestMistClientSuccess:
    def test_get_object_returns_data_on_http_200_success(self, client, success_response):
        with patch("shared.mist_client.requests.get", return_value=success_response):
            assert client.get_object("/v1/securities") == {"key": "value"}

    def test_post_list_returns_data_on_success(self, client, success_response):
        success_response.json.return_value["data"] = [{"macd": 1.0}]
        with patch("shared.mist_client.requests.post", return_value=success_response):
            assert client.post_list("/v1/indicators/macd", {"code": "000001"}) == [{"macd": 1.0}]

    def test_post_object_returns_object_payload(self, client, success_response):
        with patch("shared.mist_client.requests.post", return_value=success_response):
            assert client.post_object("/v1/security-sources", {"code": "000001"}) == {
                "key": "value"
            }

    def test_post_sends_body_as_json(self, client, success_response):
        with patch("shared.mist_client.requests.post", return_value=success_response) as mock_post:
            client.post_object("/v1/indicators/macd", {"code": "000001"})
        _, kwargs = mock_post.call_args
        assert kwargs["json"] == {"code": "000001"}


class TestMistClientShapeMismatch:
    def test_typed_helpers_reject_object_where_list_expected(self, client, success_response):
        success_response.json.return_value["data"] = {"unexpected": True}
        with (
            patch("shared.mist_client.requests.post", return_value=success_response),
            pytest.raises(MistApiContractError) as exc_info,
        ):
            client.post_list("/v1/indicators/macd", {"code": "000001"})
        assert "not a list" in str(exc_info.value)

    def test_typed_helpers_reject_list_where_object_expected(self, client, success_response):
        success_response.json.return_value["data"] = [{"unexpected": True}]
        with (
            patch("shared.mist_client.requests.post", return_value=success_response),
            pytest.raises(MistApiContractError),
        ):
            client.post_object("/v1/security-sources", {"code": "000001"})


class TestMistClientApiError:
    def test_http_200_business_rejection_raises_mist_api_error(self, client):
        resp = error_envelope(200, "BACKTEST_QUEUE_FULL", "queue full", data={"capacity": 100})
        with (
            patch("shared.mist_client.requests.post", return_value=resp),
            pytest.raises(MistApiError) as exc_info,
        ):
            client.post_object("/v1/strategy-backtests", {})
        assert exc_info.value.code == "BACKTEST_QUEUE_FULL"
        assert exc_info.value.http_status == 200
        assert exc_info.value.data == {"capacity": 100}

    def test_400_validation_error_raises_mist_api_error_with_errors(self, client):
        resp = error_envelope(
            400,
            "VALIDATION_ERROR",
            "Request validation failed",
            errors={"code": ["must not be empty"]},
        )
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiError) as exc_info,
        ):
            client.get_object("/v1/securities")
        assert exc_info.value.code == "VALIDATION_ERROR"
        assert exc_info.value.http_status == 400
        assert exc_info.value.errors == {"code": ["must not be empty"]}

    @pytest.mark.parametrize(
        "status,code",
        [(500, "INTERNAL_ERROR"), (502, "BAD_GATEWAY")],
    )
    def test_non_2xx_technical_error_raises_mist_api_error(self, client, status, code):
        resp = error_envelope(status, code, "boom")
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiError) as exc_info,
        ):
            client.get_object("/v1/securities")
        assert exc_info.value.code == code
        assert exc_info.value.http_status == status


class TestMistClientContractError:
    def test_bare_payload_raises_contract_error(self, client):
        resp = _resp([{"code": "000001"}], status=200)
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiContractError),
        ):
            client.get_object("/v1/securities")

    def test_invalid_json_raises_contract_error(self, client):
        resp = _resp(None, status=400, json_error=ValueError("not json"))
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiContractError),
        ):
            client.get_object("/v1/securities")

    def test_missing_field_envelope_raises_contract_error(self, client):
        resp = _resp(
            {
                "success": True,
                "statusCode": 200,
                "message": "SUCCESS",
                "data": [],
                # timestamp / requestId / path missing
            },
            status=200,
        )
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiContractError),
        ):
            client.get_object("/v1/securities")

    def test_status_mismatch_raises_contract_error(self, client):
        resp = _resp(
            {
                "success": False,
                "statusCode": 404,
                "code": "NOT_FOUND",
                "message": "missing",
                "timestamp": "2026-08-03T00:00:00.000Z",
                "requestId": "http-1",
                "path": "/v1/securities",
            },
            status=200,
        )
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiContractError),
        ):
            client.get_object("/v1/securities")

    def test_success_envelope_missing_data_field_raises_contract_error(self, client):
        resp = _resp(
            {
                "success": True,
                "statusCode": 200,
                "message": "SUCCESS",
                "timestamp": "2026-08-03T00:00:00.000Z",
                "requestId": "http-missing-data",
                "path": "/v1/securities",
            },
            status=200,
        )
        with (
            patch("shared.mist_client.requests.get", return_value=resp),
            pytest.raises(MistApiContractError) as exc_info,
        ):
            client.get_object("/v1/securities")
        assert "data" in str(exc_info.value).lower()

    def test_tolerates_additive_unknown_fields(self, client):
        resp = _resp(
            {
                "success": True,
                "statusCode": 200,
                "message": "SUCCESS",
                "data": [{"code": "600519"}],
                "timestamp": "2026-08-03T00:00:00.000Z",
                "requestId": "http-1",
                "path": "/v1/securities",
                "serverVersion": "1.2.3",
                "traceId": "trace-xyz",
            },
            status=200,
        )
        with patch("shared.mist_client.requests.get", return_value=resp):
            assert client.get_list("/v1/securities") == [{"code": "600519"}]


class TestMistClientNoContent:
    def test_request_no_content_accepts_204_and_returns_request_id(self, client):
        resp = MagicMock()
        resp.status_code = 204
        resp.headers.get.side_effect = lambda key, default=None: (
            "http-204" if key == "x-request-id" else default
        )
        with patch("shared.mist_client.requests.post", return_value=resp):
            request_id = client.request_no_content("POST", "/v1/example/no-content", {})
        assert request_id == "http-204"
        # json() is never invoked
        resp.json.assert_not_called()

    def test_request_no_content_fails_closed_on_non_204(self, client, success_response):
        with (
            patch("shared.mist_client.requests.post", return_value=success_response),
            pytest.raises(MistApiContractError),
        ):
            client.request_no_content("POST", "/v1/example/no-content", {})


class TestMistClientConnection:
    def test_connection_error_is_raised_on_connection_failure(self, client):
        import requests

        with (
            patch(
                "shared.mist_client.requests.get",
                side_effect=requests.ConnectionError("Connection refused"),
            ),
            pytest.raises(MistConnectionError),
        ):
            client.get_object("/v1/securities")

    def test_connection_error_is_raised_on_timeout(self, client):
        import requests

        with (
            patch("shared.mist_client.requests.get", side_effect=requests.Timeout("Timed out")),
            pytest.raises(MistConnectionError),
        ):
            client.get_object("/v1/securities")

    def test_base_url_comes_from_config(self, client):
        assert "8001" in client.base_url
