from __future__ import annotations

from fastapi.testclient import TestClient

from rag_compliance_assistant.api import dependencies
from rag_compliance_assistant.api.main import app
from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.rag.service import RagService


def test_api_health_and_query_use_mock_mode(
    rag_service: RagService,
    test_settings: Settings,
) -> None:
    app.dependency_overrides[dependencies.get_rag_service] = lambda: rag_service
    app.dependency_overrides[dependencies.get_settings] = lambda: test_settings
    client = TestClient(app)

    health = client.get("/health")
    query = client.post(
        "/query",
        json={"query": "Can employees paste confidential customer data into public AI tools?"},
    )

    app.dependency_overrides.clear()

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert query.status_code == 200
    body = query.json()
    assert body["providers"]["llm"] == "mock"
    assert body["citations"]
    assert body["retrieved_chunks"]
