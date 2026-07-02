from unittest.mock import MagicMock

import pytest

from shared.kline_runner import (
    INTRADAY_PERIODS,
    run_kline_query,
)
from shared.mist_client import MistApiError, MistClient


def test_run_kline_query_collects_intraday_with_period_specific_body():
    client = MagicMock(spec=MistClient)
    kline_data = [{"symbol": "600519.SH", "open": 1700}]
    client.post.side_effect = [
        MistApiError("Index information not found", 400),
        {"code": "600519", "name": "贵州茅台"},
        {"code": "600519"},
        {"code": "600519", "period": 60, "count": 1},
        kline_data,
    ]
    client.get.side_effect = [
        MistApiError("Security with code 600519 not found", 404),
    ]

    result = run_kline_query(
        client=client,
        code="600519.SH",
        period="60min",
        start_date="2026-06-26 09:30:00",
        end_date="2026-06-26 15:00:00",
        source="tdx",
        name="贵州茅台",
        allowed_periods=INTRADAY_PERIODS,
    )

    assert result == kline_data
    assert client.post.call_args_list[3].args == (
        "/v1/collector/collect",
        {
            "code": "600519",
            "period": 60,
            "startDate": "2026-06-26 09:30:00",
            "endDate": "2026-06-26 15:00:00",
            "source": "tdx",
        },
    )
    assert client.post.call_args_list[4].args[1]["period"] == 60


def test_run_kline_query_collects_daily_with_daily_body():
    client = MagicMock(spec=MistClient)
    kline_data = [{"symbol": "600519.SH", "open": 1700}]
    client.post.side_effect = [
        [],
        {"code": "600519", "name": "贵州茅台"},
        {"code": "600519"},
        {"code": "600519", "period": 1440, "count": 1},
        kline_data,
    ]
    client.get.side_effect = [
        MistApiError("Security with code 600519 not found", 404),
    ]

    result = run_kline_query(
        client=client,
        code="600519.SH",
        period="daily",
        start_date="2026-06-21",
        end_date="2026-06-28",
        source="tdx",
        name="贵州茅台",
        allowed_periods={1440},
    )

    assert result == kline_data
    assert client.post.call_args_list[3].args == (
        "/v1/collector/collect",
        {
            "code": "600519",
            "period": 1440,
            "startDate": "2026-06-21",
            "endDate": "2026-06-28",
            "source": "tdx",
        },
    )


def test_run_kline_query_rejects_disallowed_period():
    client = MagicMock(spec=MistClient)

    with pytest.raises(SystemExit) as exc_info:
        run_kline_query(
            client=client,
            code="600519.SH",
            period="daily",
            start_date="2026-06-21",
            end_date="2026-06-28",
            source="tdx",
            allowed_periods=INTRADAY_PERIODS,
            invalid_period_message="Error: period must be intraday",
        )

    assert exc_info.value.code == 1
    client.post.assert_not_called()
