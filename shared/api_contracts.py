from dataclasses import dataclass


@dataclass(frozen=True)
class ApiEndpoints:
    security_all: str = "/security/v1/all"
    security_initialize: str = "/security/v1/initialize"
    security_sources: str = "/security/v1/sources"
    indicator_k: str = "/indicator/k"
    collector_collect: str = "/v1/collector/collect"
    strategy_alert_events: str = "/v1/strategy-alert-events"

    def security_detail(self, code: str) -> str:
        return f"/security/v1/{code}"

    def indicator(self, name: str) -> str:
        return f"/indicator/{name}"

    def chan(self, name: str) -> str:
        return f"/chan/{name}"

    def strategy_alert_event_delivery(self, alert_event_id: int, outcome: str) -> str:
        return f"{self.strategy_alert_events}/{alert_event_id}/{outcome}"


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
