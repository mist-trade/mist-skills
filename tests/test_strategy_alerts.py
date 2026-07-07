from shared.strategy_alerts import (
    list_pending_strategy_alerts,
    mark_strategy_alert_delivered,
    mark_strategy_alert_failed,
)


class FakeMistClient:
    def __init__(self):
        self.calls = []

    def get_list(self, path):
        self.calls.append(("GET_LIST", path, None))
        return [{"id": 1, "status": "pending"}]

    def post_object(self, path, body):
        self.calls.append(("POST_OBJECT", path, body))
        return {"id": 1, "status": path.rsplit("/", 1)[-1]}


def assert_no_datasource_or_raw_paths(client):
    called_paths = [path for _, path, _ in client.calls]

    assert all("/datasource/" not in path for path in called_paths)
    assert all("/raw" not in path for path in called_paths)
    assert all("/provider" not in path for path in called_paths)


def test_list_pending_strategy_alerts_uses_backend_alert_event_api():
    client = FakeMistClient()

    alerts = list_pending_strategy_alerts(client=client)

    assert alerts == [{"id": 1, "status": "pending"}]
    assert client.calls == [
        ("GET_LIST", "/v1/strategy-alert-events?status=pending", None)
    ]
    assert_no_datasource_or_raw_paths(client)


def test_mark_strategy_alert_delivered_uses_backend_delivery_api():
    client = FakeMistClient()

    event = mark_strategy_alert_delivered(
        1,
        delivery_result={"channel": "astrbot", "messageId": "msg-1"},
        client=client,
    )

    assert event == {"id": 1, "status": "delivered"}
    assert client.calls == [
        (
            "POST_OBJECT",
            "/v1/strategy-alert-events/1/delivered",
            {"deliveryResult": {"channel": "astrbot", "messageId": "msg-1"}},
        )
    ]
    assert_no_datasource_or_raw_paths(client)


def test_mark_strategy_alert_failed_uses_backend_failure_api():
    client = FakeMistClient()

    event = mark_strategy_alert_failed(
        1,
        delivery_result={"channel": "astrbot", "error": "bot unavailable"},
        client=client,
    )

    assert event == {"id": 1, "status": "failed"}
    assert client.calls == [
        (
            "POST_OBJECT",
            "/v1/strategy-alert-events/1/failed",
            {"deliveryResult": {"channel": "astrbot", "error": "bot unavailable"}},
        )
    ]
    assert_no_datasource_or_raw_paths(client)
