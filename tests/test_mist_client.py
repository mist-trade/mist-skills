from unittest.mock import MagicMock, patch

import pytest

from shared.mist_client import MistApiError, MistClient, MistConnectionError


@pytest.fixture
def client():
    return MistClient()


@pytest.fixture
def success_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "success": True,
        "statusCode": 200,
        "message": "SUCCESS",
        "data": {"key": "value"},
        "timestamp": "2026-04-13T00:00:00Z",
        "requestId": "req-1",
    }
    return resp


def test_get_success(client, success_response):
    """GET request returns data on success."""
    with patch("shared.mist_client.requests.get", return_value=success_response):
        result = client.get("/security/v1/all")
    assert result == {"key": "value"}


def test_post_success(client, success_response):
    """POST request returns data on success."""
    success_response.json.return_value["data"] = [{"macd": 1.0}]
    with patch("shared.mist_client.requests.post", return_value=success_response):
        result = client.post("/indicator/macd", {"code": "000001", "period": "daily"})
    assert result == [{"macd": 1.0}]


def test_post_sends_json_body(client, success_response):
    """POST sends body as JSON."""
    with patch("shared.mist_client.requests.post", return_value=success_response) as mock_post:
        client.post("/indicator/macd", {"code": "000001"})
    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"code": "000001"}


def test_api_error_on_success_false(client):
    """Raises MistApiError when response has success=false."""
    resp = MagicMock()
    resp.status_code = 400
    resp.json.return_value = {
        "success": False,
        "statusCode": 2001,
        "message": "Symbol not found",
        "data": None,
        "timestamp": "...",
        "requestId": "req-2",
    }
    with (
        patch("shared.mist_client.requests.get", return_value=resp),
        pytest.raises(MistApiError) as exc_info,
    ):
        client.get("/security/v1/INVALID")
    assert "Symbol not found" in str(exc_info.value)
    assert exc_info.value.error_code == 2001


def test_success_without_data_raises_api_error(client):
    """Malformed success envelopes are surfaced as MistApiError, not KeyError."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "success": True,
        "statusCode": 200,
        "message": "SUCCESS",
        "timestamp": "2026-04-13T00:00:00Z",
        "requestId": "req-missing-data",
    }

    with (
        patch("shared.mist_client.requests.get", return_value=resp),
        pytest.raises(MistApiError) as exc_info,
    ):
        client.get("/security/v1/all")

    assert "missing data" in str(exc_info.value).lower()
    assert exc_info.value.error_code == 200


def test_connection_error(client):
    """Raises MistConnectionError on connection failure."""
    import requests

    with (
        patch(
            "shared.mist_client.requests.get",
            side_effect=requests.ConnectionError("Connection refused"),
        ),
        pytest.raises(MistConnectionError),
    ):
        client.get("/security/v1/all")


def test_timeout_error(client):
    """Raises MistConnectionError on timeout."""
    import requests

    with (
        patch("shared.mist_client.requests.get", side_effect=requests.Timeout("Timed out")),
        pytest.raises(MistConnectionError),
    ):
        client.get("/security/v1/all")


def test_base_url_from_config(client):
    """Client uses base URL from config."""
    assert "8001" in client.base_url
