import json
import sys
import os
import pytest
from unittest.mock import ANY, patch, MagicMock
from shared.mist_client import MistClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "technical-indicators", "scripts"))


def _mock_client(data):
    client = MagicMock(spec=MistClient)
    client.post.return_value = data
    return client


@pytest.fixture
def macd_data():
    return [
        {"macd": 10.5, "signal": 8.3, "histogram": 2.2, "symbol": "000001.SH", "time": "2026-04-10", "close": 3310},
        {"macd": 11.0, "signal": 9.0, "histogram": 2.0, "symbol": "000001.SH", "time": "2026-04-11", "close": 3320},
    ]


@pytest.fixture
def kdj_data():
    return [
        {"k": 75.2, "d": 70.1, "j": 85.4, "symbol": "000001.SH", "time": "2026-04-10", "close": 3310},
    ]


@pytest.fixture
def rsi_data():
    return [
        {"rsi": 65.3, "symbol": "000001.SH", "time": "2026-04-10", "close": 3310},
    ]


def test_macd(macd_data):
    import macd
    with patch.object(macd, "MistClient", return_value=_mock_client(macd_data)):
        result = macd.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert len(result) == 2
    assert result[0]["macd"] == 10.5


def test_macd_endpoint(macd_data):
    import macd
    client = _mock_client(macd_data)
    with patch.object(macd, "MistClient", return_value=client):
        macd.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    client.post.assert_called_once()
    assert client.post.call_args[0][0] == "/indicator/macd"


def test_kdj(kdj_data):
    import kdj
    with patch.object(kdj, "MistClient", return_value=_mock_client(kdj_data)):
        result = kdj.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert result[0]["k"] == 75.2


def test_kdj_endpoint(kdj_data):
    import kdj
    client = _mock_client(kdj_data)
    with patch.object(kdj, "MistClient", return_value=client):
        kdj.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert client.post.call_args[0][0] == "/indicator/kdj"


def test_rsi(rsi_data):
    import rsi
    with patch.object(rsi, "MistClient", return_value=_mock_client(rsi_data)):
        result = rsi.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert result[0]["rsi"] == 65.3


def test_rsi_endpoint(rsi_data):
    import rsi
    client = _mock_client(rsi_data)
    with patch.object(rsi, "MistClient", return_value=client):
        rsi.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert client.post.call_args[0][0] == "/indicator/rsi"


def test_indicator_body_params(macd_data):
    """Scripts pass all optional params when provided."""
    import macd
    client = _mock_client(macd_data)
    with patch.object(macd, "MistClient", return_value=client):
        macd.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13", source="tdx")
    body = client.post.call_args[0][1]
    assert body["code"] == "000001"
    assert body["period"] == 1440
    assert body["startDate"] == "2026-01-01"
    assert body["endDate"] == "2026-04-13"
    assert body["source"] == "tdx"


@pytest.mark.parametrize(
    ("module_name", "endpoint"),
    [
        ("macd", "/indicator/macd"),
        ("kdj", "/indicator/kdj"),
        ("rsi", "/indicator/rsi"),
    ],
)
def test_indicator_scripts_delegate_to_shared_runner(module_name, endpoint):
    module = __import__(module_name)
    calls = []

    def fake_run_simple_post(**kwargs):
        calls.append(kwargs)
        return [{"ok": True}]

    with patch.object(module, "run_simple_post", side_effect=fake_run_simple_post):
        result = module.main(
            code="000001.SH",
            period="daily",
            start_date="2026-01-01",
            end_date="2026-04-13",
            source="tdx",
        )

    assert result == [{"ok": True}]
    assert calls == [
        {
            "endpoint": endpoint,
            "code": "000001.SH",
            "period": "daily",
            "start_date": "2026-01-01",
            "end_date": "2026-04-13",
            "source": "tdx",
            "client": ANY,
        }
    ]
