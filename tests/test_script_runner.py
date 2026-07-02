from unittest.mock import MagicMock

import pytest

from shared.mist_client import MistApiError, MistConnectionError
from shared.script_runner import build_analysis_body, run_cli, run_simple_post


def test_build_analysis_body_normalizes_code_period_and_source():
    body = build_analysis_body(
        code="000001.SH",
        period="daily",
        start_date="2026-01-01",
        end_date="2026-04-13",
        source="tdx",
    )

    assert body == {
        "code": "000001",
        "period": 1440,
        "startDate": "2026-01-01",
        "endDate": "2026-04-13",
        "source": "tdx",
    }


def test_run_simple_post_calls_expected_endpoint_with_shared_body():
    client = MagicMock()
    client.post.return_value = [{"macd": 1.0}]

    result = run_simple_post(
        endpoint="/indicator/macd",
        code="000001.SH",
        period="daily",
        start_date="2026-01-01",
        end_date="2026-04-13",
        source="tdx",
        client=client,
    )

    assert result == [{"macd": 1.0}]
    client.post.assert_called_once_with(
        "/indicator/macd",
        {
            "code": "000001",
            "period": 1440,
            "startDate": "2026-01-01",
            "endDate": "2026-04-13",
            "source": "tdx",
        },
    )


def test_run_cli_catches_connection_error(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_cli(lambda: (_ for _ in ()).throw(MistConnectionError("dial failed")))

    assert exc_info.value.code == 1
    assert "Connection error: dial failed" in capsys.readouterr().err


def test_run_cli_catches_api_error(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_cli(lambda: (_ for _ in ()).throw(MistApiError("bad request", 400)))

    assert exc_info.value.code == 1
    assert "Mist API error (400): bad request" in capsys.readouterr().err
