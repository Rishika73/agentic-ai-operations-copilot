import os

from fastapi.testclient import TestClient

from app.main import app


TEST_API_KEY = "test-api-key"
os.environ["APP_API_KEY"] = TEST_API_KEY

AUTH_HEADERS = {
    "X-API-Key": TEST_API_KEY,
}

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "Agentic AI Operations Copilot"
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_knowledge_request(monkeypatch):
    def fake_invoke(state, config=None):
        return {
            "route": "knowledge",
            "final_answer": "Critical incident policy summary.",
            "proposed_action": {
                "action_type": "no_action",
                "description": "No operational action required.",
            },
            "requires_approval": False,
            "approval_status": "not_required",
            "action_result": {
                "status": "no_action",
            },
        }

    monkeypatch.setattr(
        "app.main.agent_graph.invoke",
        fake_invoke,
    )

    response = client.post(
        "/ask",
        headers=AUTH_HEADERS,
        json={
            "query": "What is the policy for critical incident response?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route"] == "knowledge"
    assert data["requires_approval"] is False
    assert data["status"] == "completed"


def test_incident_request_requires_approval(monkeypatch):
    def fake_invoke(state, config=None):
        return {
            "route": "incident",
            "final_answer": "Three open incidents.",
            "proposed_action": {
                "action_type": "incident_escalation",
            },
            "requires_approval": True,
            "approval_status": "pending",
            "action_result": None,
            "__interrupt__": [
                {
                    "value": {
                        "message": "Human approval required"
                    }
                }
            ],
        }

    monkeypatch.setattr(
        "app.main.agent_graph.invoke",
        fake_invoke,
    )

    response = client.post(
        "/ask",
        headers=AUTH_HEADERS,
        json={
            "query": "What open incidents do we have?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route"] == "incident"
    assert data["requires_approval"] is True
    assert data["status"] == "awaiting_approval"


def test_approval_endpoint(monkeypatch):
    def fake_invoke(command, config=None):
        return {
            "approval_status": "approved",
            "action_result": {
                "status": "executed",
                "action_type": "incident_escalation",
            },
        }

    monkeypatch.setattr(
        "app.main.agent_graph.invoke",
        fake_invoke,
    )

    response = client.post(
        "/approve",
        headers=AUTH_HEADERS,
        json={
            "thread_id": "test-thread",
            "decision": "approve",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_status"] == "approved"
    assert data["action_result"]["status"] == "executed"
    assert data["status"] == "completed"
