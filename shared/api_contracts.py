from dataclasses import dataclass


@dataclass(frozen=True)
class ApiEndpoints:
    security_all: str = "/security/v1/all"
    security_initialize: str = "/security/v1/initialize"
    security_sources: str = "/security/v1/sources"
    indicator_k: str = "/indicator/k"
    collector_collect: str = "/v1/collector/collect"

    def security_detail(self, code: str) -> str:
        return f"/security/v1/{code}"

    def indicator(self, name: str) -> str:
        return f"/indicator/{name}"

    def chan(self, name: str) -> str:
        return f"/chan/{name}"


API_ENDPOINTS = ApiEndpoints()

FIELD_CODE = "code"
FIELD_ENABLED = "enabled"
FIELD_END_DATE = "endDate"
FIELD_FORMAT_CODE = "formatCode"
FIELD_NAME = "name"
FIELD_PERIOD = "period"
FIELD_PRIORITY = "priority"
FIELD_SOURCE = "source"
FIELD_START_DATE = "startDate"
FIELD_TYPE = "type"

SECURITY_TYPE_STOCK = "STOCK"
SECURITY_SOURCE_PRIORITY = 100
KLINE_RETRY_STATUS_CODES = frozenset({400, 404})
SOURCE_HELP_TEXT = "Data source (ef/tdx/mqmt)"
