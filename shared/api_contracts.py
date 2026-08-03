from dataclasses import dataclass


@dataclass(frozen=True)
class ApiEndpoints:
    security_all: str = "/v1/securities"
    security_initialize: str = "/v1/securities"
    security_sources: str = "/v1/security-sources"
    indicator_k: str = "/v1/indicators/k"
    collector_collect: str = "/v1/collector/collect"
    strategy_alert_events: str = "/v1/strategy-alert-events"

    def security_detail(self, code: str) -> str:
        return f"/v1/securities/{code}"

    def indicator(self, name: str) -> str:
        return f"/v1/indicators/{name}"

    def chan(self, name: str) -> str:
        return f"/v1/chan/{name}"

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

#: Stable backend error codes that may trigger an automatic K-line collection.
#:
#: These replace the former HTTP-status allowlist ``{400, 404}`` and are derived
#: from the archived ``standardize-service-boundary-contracts`` backend contract
#: rather than guessed from a generic HTTP status:
#:
#: * ``BAD_REQUEST`` - ``POST /v1/indicators/k`` reports a missing security via a
#:   thrown ``HttpException(BAD_REQUEST)`` (``indicator.service.ts``); it is the
#:   signal that the requested K-line window is not yet present and should be
#:   collected.
#: * ``NOT_FOUND`` - ``GET /v1/securities/:code``, ``POST /v1/security-sources``
#:   and ``POST /v1/collector/collect`` report a missing security via a thrown
#:   ``NotFoundException``.
#:
#: The set intentionally excludes ``VALIDATION_ERROR`` (also HTTP 400 under the
#: old status allowlist) because a request-shape validation failure is a client
#: bug, not a "needs collection" signal. This preserves the prior auto-collection
#: business scope without widening it.
KLINE_COLLECT_ERROR_CODES = frozenset({"BAD_REQUEST", "NOT_FOUND"})
SOURCE_HELP_TEXT = "Data source (ef/tdx/mqmt)"
