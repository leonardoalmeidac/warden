import pytest
from unittest.mock import patch

VALID_PAYLOAD = {
    "project_id": "payments-api",
    "environment_id": "prod",
    "severity": "high",
    "signal": "P99 latency spiked to 4s after the 14:30 deploy",
    "context": {
        "last_deploy": "v2.3.1",
        "cpu_usage": "85%",
        "error_rate": "12%"
    },
    "timestamp": "2024-04-03T14:45:00Z"
}

MOCK_DECISION = {
    "action": "rollback",
    "confidence": 0.8,
    "reasoning": "Recent deploy caused latency spike.",
    "safe_to_auto": False
}

def test_ingest_event_valid_payload(client):
    with patch('src.api.events.reason') as mock_reason:
        mock_reason.return_value = type("Decision", (), {
            "id": "decision-id",
            "action": "rollback",
            "confidence": 0.8,
            "reasoning": "Recent deploy caused latency spike.",
            "safe_to_auto": False,
            "executed": False,
        })()

        response = client.post("/events/", json=VALID_PAYLOAD)
        assert response.status_code == 200
        assert response.json()["status"] == "pending_approval"

def test_ingest_event_invalid_severity(client):
    payload = {**VALID_PAYLOAD, "severity": "extreme"}
    response = client.post("/events/", json=payload)
    assert response.status_code == 422


def test_ingest_event_invalid_environment(client):
    payload = {**VALID_PAYLOAD, "environment_id": "staging"}
    response = client.post("/events/", json=payload)
    assert response.status_code == 422


def test_ingest_event_missing_fields(client):
    response = client.post("/events/", json={"project_id": "payments-api"})
    assert response.status_code == 422


def test_ingest_event_safe_to_auto_true(client):
    with patch("src.api.events.reason") as mock_reason:
        with patch("src.api.events.execute_action") as mock_execute:
            mock_execute.return_value = {"action": "restart", "status": "executed", "detail": "Restarted"}
            mock_reason.return_value = type("Decision", (), {
                "id": "decision-id",
                "action": "restart",
                "confidence": 0.9,
                "reasoning": "Service is unresponsive.",
                "safe_to_auto": True,
                "executed": False,
            })()

            payload = {**VALID_PAYLOAD, "environment_id": "dev", "severity": "low"}
            response = client.post("/events/", json=payload)
            assert response.status_code == 200
            assert response.json()["status"] == "processed"
