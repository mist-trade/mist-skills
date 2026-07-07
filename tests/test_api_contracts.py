import importlib


def test_api_contracts_define_current_backend_paths():
    contracts = importlib.import_module("shared.api_contracts")

    API_ENDPOINTS = contracts.API_ENDPOINTS

    assert API_ENDPOINTS.security_all == "/v1/securities"
    assert API_ENDPOINTS.security_detail("600519") == "/v1/securities/600519"
    assert API_ENDPOINTS.security_initialize == "/v1/securities"
    assert API_ENDPOINTS.security_sources == "/v1/security-sources"
    assert API_ENDPOINTS.indicator_k == "/v1/indicators/k"
    assert API_ENDPOINTS.indicator("macd") == "/v1/indicators/macd"
    assert API_ENDPOINTS.chan("merge-k") == "/v1/chan/merge-k"
    assert API_ENDPOINTS.collector_collect == "/v1/collector/collect"
    assert API_ENDPOINTS.strategy_alert_events == "/v1/strategy-alert-events"
    assert (
        API_ENDPOINTS.strategy_alert_event_delivery(1, "delivered")
        == "/v1/strategy-alert-events/1/delivered"
    )


def test_api_contracts_define_payload_fields_and_retry_codes():
    contracts = importlib.import_module("shared.api_contracts")

    assert contracts.FIELD_CODE == "code"
    assert contracts.FIELD_PERIOD == "period"
    assert contracts.FIELD_START_DATE == "startDate"
    assert contracts.FIELD_END_DATE == "endDate"
    assert contracts.FIELD_SOURCE == "source"
    assert contracts.FIELD_FORMAT_CODE == "formatCode"
    assert contracts.FIELD_PRIORITY == "priority"
    assert contracts.SECURITY_TYPE_STOCK == "STOCK"
    assert contracts.SECURITY_SOURCE_PRIORITY == 100
    assert frozenset({400, 404}) == contracts.KLINE_RETRY_STATUS_CODES
