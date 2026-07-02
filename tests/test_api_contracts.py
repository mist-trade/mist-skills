import importlib


def test_api_contracts_define_current_backend_paths():
    contracts = importlib.import_module("shared.api_contracts")

    API_ENDPOINTS = contracts.API_ENDPOINTS

    assert API_ENDPOINTS.security_all == "/security/v1/all"
    assert API_ENDPOINTS.security_detail("600519") == "/security/v1/600519"
    assert API_ENDPOINTS.security_initialize == "/security/v1/initialize"
    assert API_ENDPOINTS.security_sources == "/security/v1/sources"
    assert API_ENDPOINTS.indicator_k == "/indicator/k"
    assert API_ENDPOINTS.indicator("macd") == "/indicator/macd"
    assert API_ENDPOINTS.chan("merge-k") == "/chan/merge-k"
    assert API_ENDPOINTS.collector_collect == "/v1/collector/collect"


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
