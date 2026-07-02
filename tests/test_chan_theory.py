from unittest.mock import ANY, MagicMock, patch

import pytest

from shared.mist_client import MistClient
from tests.script_loader import load_skill_script


def _mock_client(data):
    client = MagicMock(spec=MistClient)
    client.post.return_value = data
    return client


@pytest.fixture
def merged_k_data():
    return [
        {
            "startTime": "2026-04-10",
            "endTime": "2026-04-11",
            "highest": 3320,
            "lowest": 3290,
            "trend": "UP",
            "mergedCount": 2,
        },
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
    merge_k = load_skill_script("chan-theory", "merge_k")
    with patch.object(merge_k, "MistClient", return_value=_mock_client(merged_k_data)):
        result = merge_k.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert result[0]["trend"] == "UP"


def test_merge_k_endpoint(merged_k_data):
    merge_k = load_skill_script("chan-theory", "merge_k")
    client = _mock_client(merged_k_data)
    with patch.object(merge_k, "MistClient", return_value=client):
        merge_k.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert client.post.call_args[0][0] == "/chan/merge-k"


def test_create_bi(bi_data):
    create_bi = load_skill_script("chan-theory", "create_bi")
    with patch.object(create_bi, "MistClient", return_value=_mock_client(bi_data)):
        result = create_bi.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert len(result) > 0


def test_create_bi_endpoint(bi_data):
    create_bi = load_skill_script("chan-theory", "create_bi")
    client = _mock_client(bi_data)
    with patch.object(create_bi, "MistClient", return_value=client):
        create_bi.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert client.post.call_args[0][0] == "/chan/bi"


def test_get_fenxing(fenxing_data):
    get_fenxing = load_skill_script("chan-theory", "get_fenxing")
    with patch.object(get_fenxing, "MistClient", return_value=_mock_client(fenxing_data)):
        result = get_fenxing.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert result[0]["type"] == "TOP"


def test_get_fenxing_endpoint(fenxing_data):
    get_fenxing = load_skill_script("chan-theory", "get_fenxing")
    client = _mock_client(fenxing_data)
    with patch.object(get_fenxing, "MistClient", return_value=client):
        get_fenxing.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert client.post.call_args[0][0] == "/chan/fenxing"


def test_analyze_chan(channel_data):
    analyze_chan = load_skill_script("chan-theory", "analyze_chan")
    with patch.object(analyze_chan, "MistClient", return_value=_mock_client(channel_data)):
        result = analyze_chan.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
    assert len(result) > 0


def test_analyze_chan_endpoint(channel_data):
    analyze_chan = load_skill_script("chan-theory", "analyze_chan")
    client = _mock_client(channel_data)
    with patch.object(analyze_chan, "MistClient", return_value=client):
        analyze_chan.main(
            code="000001.SH", period="daily", start_date="2026-01-01", end_date="2026-04-13"
        )
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
    module = load_skill_script("chan-theory", module_name)
    client = _mock_client(merged_k_data)
    with patch.object(module, "MistClient", return_value=client):
        module.main(
            code="000001.SH",
            period="daily",
            start_date="2026-01-01",
            end_date="2026-04-13",
            source="tdx",
        )
    assert client.post.call_args[0][0] == endpoint
    body = client.post.call_args[0][1]
    assert body["code"] == "000001"
    assert body["period"] == 1440
    assert body["startDate"] == "2026-01-01"
    assert body["endDate"] == "2026-04-13"
    assert body["source"] == "tdx"


@pytest.mark.parametrize(
    ("module_name", "endpoint"),
    [
        ("merge_k", "/chan/merge-k"),
        ("create_bi", "/chan/bi"),
        ("get_fenxing", "/chan/fenxing"),
        ("analyze_chan", "/chan/channel"),
    ],
)
def test_chan_scripts_delegate_to_shared_runner(module_name, endpoint):
    module = load_skill_script("chan-theory", module_name)
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
