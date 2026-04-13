import json
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from shared.mist_client import MistClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "data-query", "scripts"))


def _mock_client_success(data):
    client = MagicMock(spec=MistClient)
    client.get.return_value = data
    client.post.return_value = data
    return client


@pytest.fixture
def securities_data():
    return [
        {"id": 1, "code": "000001.SH", "name": "上证指数", "type": "INDEX"},
        {"id": 2, "code": "399006.SZ", "name": "创业板指", "type": "INDEX"},
    ]


def _get_symbol(item):
    """Get symbol from security data (uses 'code' field from REST API)."""
    return item.get("code") or item.get("symbol")


@pytest.fixture
def kline_data():
    return [
        {"id": 1, "symbol": "000001.SH", "time": "2026-04-13", "open": 3300, "close": 3310, "highest": 3320, "lowest": 3290, "amount": 100000},
    ]


def test_list_indices(securities_data):
    import list_indices
    with patch.object(list_indices, "MistClient", return_value=_mock_client_success(securities_data)):
        result = list_indices.main()
    assert len(result) == 2
    assert _get_symbol(result[0]) == "000001.SH"


def test_get_index_info(securities_data):
    import get_index_info
    data = securities_data[0]
    with patch.object(get_index_info, "MistClient", return_value=_mock_client_success(data)):
        result = get_index_info.main(code="000001.SH")
    assert _get_symbol(result) == "000001.SH"


def test_get_kline_data(kline_data):
    import get_kline_data
    with patch.object(get_kline_data, "MistClient", return_value=_mock_client_success(kline_data)):
        result = get_kline_data.main(code="000001.SH", period="5min", start_date="2026-01-01", end_date="2026-04-13")
    assert len(result) == 1
    assert result[0]["open"] == 3300


def test_get_kline_data_rejects_daily():
    """get_kline_data should reject daily period."""
    import get_kline_data
    with pytest.raises(SystemExit):
        get_kline_data.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")


def test_get_daily_kline(kline_data):
    import get_daily_kline
    with patch.object(get_daily_kline, "MistClient", return_value=_mock_client_success(kline_data)):
        result = get_daily_kline.main(code="000001.SH", start_date="2026-01-01", end_date="2026-04-13")
    assert len(result) == 1


def test_get_daily_kline_sends_daily_period(kline_data):
    """get_daily_kline hardcodes period=daily."""
    import get_daily_kline
    client = _mock_client_success(kline_data)
    with patch.object(get_daily_kline, "MistClient", return_value=client):
        get_daily_kline.main(code="000001.SH", start_date="2026-01-01", end_date="2026-04-13")
    client.post.assert_called_once()
    call_args = client.post.call_args
    assert call_args[0][1]["period"] == "daily"
