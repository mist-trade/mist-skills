import sys
import os
import importlib
import pytest
from unittest.mock import patch, MagicMock
from shared.mist_client import MistClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "chan-theory", "scripts"))


def _mock_client(data):
    client = MagicMock(spec=MistClient)
    client.post.return_value = data
    return client


@pytest.fixture
def merged_k_data():
    return [
        {"startTime": "2026-04-10", "endTime": "2026-04-11", "highest": 3320, "lowest": 3290, "trend": "UP", "mergedCount": 2},
    ]


@pytest.fixture
def bi_data():
    return [{"k": [{"id": 1, "highest": 3320, "lowest": 3290}]}]


@pytest.fixture
def fenxing_data():
    return [{"type": "TOP", "price": 3320, "time": "2026-04-10"}]


@pytest.fixture
def channel_data():
    return [{"bi": [{"id": 1, "direction": "UP"}]}]


def test_merge_k(merged_k_data):
    import merge_k
    with patch.object(merge_k, "MistClient", return_value=_mock_client(merged_k_data)):
        result = merge_k.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert result[0]["trend"] == "UP"


def test_merge_k_endpoint(merged_k_data):
    import merge_k
    client = _mock_client(merged_k_data)
    with patch.object(merge_k, "MistClient", return_value=client):
        merge_k.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert client.post.call_args[0][0] == "/chan/merge-k"


def test_create_bi(bi_data):
    import create_bi
    with patch.object(create_bi, "MistClient", return_value=_mock_client(bi_data)):
        result = create_bi.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert len(result) > 0


def test_create_bi_endpoint(bi_data):
    import create_bi
    client = _mock_client(bi_data)
    with patch.object(create_bi, "MistClient", return_value=client):
        create_bi.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert client.post.call_args[0][0] == "/chan/bi"


def test_get_fenxing(fenxing_data):
    import get_fenxing
    with patch.object(get_fenxing, "MistClient", return_value=_mock_client(fenxing_data)):
        result = get_fenxing.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert result[0]["type"] == "TOP"


def test_get_fenxing_endpoint(fenxing_data):
    import get_fenxing
    client = _mock_client(fenxing_data)
    with patch.object(get_fenxing, "MistClient", return_value=client):
        get_fenxing.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert client.post.call_args[0][0] == "/chan/fenxing"


def test_analyze_chan(channel_data):
    import analyze_chan
    with patch.object(analyze_chan, "MistClient", return_value=_mock_client(channel_data)):
        result = analyze_chan.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert len(result) > 0


def test_analyze_chan_endpoint(channel_data):
    import analyze_chan
    client = _mock_client(channel_data)
    with patch.object(analyze_chan, "MistClient", return_value=client):
        analyze_chan.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13")
    assert client.post.call_args[0][0] == "/chan/channel"


@pytest.mark.parametrize(
    ("module_name", "endpoint"),
    [
        ("merge_k", "/chan/merge-k"),
        ("create_bi", "/chan/bi"),
        ("get_fenxing", "/chan/fenxing"),
        ("analyze_chan", "/chan/channel"),
    ],
)
def test_chan_body_params(module_name, endpoint, merged_k_data):
    """Chan scripts normalize suffixed A-share codes and pass all optional params."""
    module = importlib.import_module(module_name)
    client = _mock_client(merged_k_data)
    with patch.object(module, "MistClient", return_value=client):
        module.main(code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13", source="tdx")
    assert client.post.call_args[0][0] == endpoint
    body = client.post.call_args[0][1]
    assert body["code"] == "000001"
    assert body["period"] == 1440
    assert body["startDate"] == "2026-01-01"
    assert body["endDate"] == "2026-04-13"
    assert body["source"] == "tdx"
