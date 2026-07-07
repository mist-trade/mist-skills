from typing import Protocol

from shared.api_contracts import API_ENDPOINTS
from shared.mist_client import JsonArray, JsonObject, MistClient


class StrategyAlertClient(Protocol):
    def get_list(self, path: str) -> JsonArray: ...

    def post_object(self, path: str, body: JsonObject) -> JsonObject: ...


def _resolve_client(client: StrategyAlertClient | None) -> StrategyAlertClient:
    return client or MistClient()


def _delivery_body(delivery_result: JsonObject | None) -> JsonObject:
    if delivery_result is None:
        return {}
    return {"deliveryResult": delivery_result}


def list_pending_strategy_alerts(
    client: StrategyAlertClient | None = None,
) -> JsonArray:
    resolved_client = _resolve_client(client)
    return resolved_client.get_list(f"{API_ENDPOINTS.strategy_alert_events}?status=pending")


def mark_strategy_alert_delivered(
    alert_event_id: int,
    delivery_result: JsonObject | None = None,
    client: StrategyAlertClient | None = None,
) -> JsonObject:
    resolved_client = _resolve_client(client)
    return resolved_client.post_object(
        API_ENDPOINTS.strategy_alert_event_delivery(alert_event_id, "delivered"),
        _delivery_body(delivery_result),
    )


def mark_strategy_alert_failed(
    alert_event_id: int,
    delivery_result: JsonObject | None = None,
    client: StrategyAlertClient | None = None,
) -> JsonObject:
    resolved_client = _resolve_client(client)
    return resolved_client.post_object(
        API_ENDPOINTS.strategy_alert_event_delivery(alert_event_id, "failed"),
        _delivery_body(delivery_result),
    )
