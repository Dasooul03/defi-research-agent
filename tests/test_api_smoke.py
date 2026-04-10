from __future__ import annotations

from fastapi.testclient import TestClient

import src.web.routes.analyze as analyze_route
import src.web.routes.chat as chat_route
import src.web.routes.report as report_route
from src.main import app

client = TestClient(app)


def test_health_happy_path() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_error_path_method_not_allowed() -> None:
    response = client.post("/health")

    assert response.status_code == 405


def test_chat_happy_path() -> None:
    response = client.post("/chat", json={"query": "price of ETH and tvl of uniswap"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert "route" in payload["data"]
    assert "result" in payload["data"]
    assert "answer" in payload["data"]


def test_chat_stream_happy_path() -> None:
    response = client.post("/chat/stream", json={"query": "price of ETH"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "\"type\":\"done\"" in response.text


def test_chat_error_path_internal_error(monkeypatch) -> None:
    def _raise_error(*_args, **_kwargs):
        raise RuntimeError("chat-boom")

    monkeypatch.setattr(chat_route.orchestrator, "run_chat", _raise_error)

    response = client.post("/chat", json={"query": "hello"})

    assert response.status_code == 500
    assert response.json() == {"detail": "chat-boom"}


def test_analyze_happy_path() -> None:
    response = client.post(
        "/analyze",
        json={"query": "analyze aave risk", "protocol": "aave"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert "data" in payload["data"]
    assert "research" in payload["data"]


def test_analyze_error_path_internal_error(monkeypatch) -> None:
    def _raise_error(*_args, **_kwargs):
        raise RuntimeError("analyze-boom")

    monkeypatch.setattr(analyze_route.orchestrator, "run_analysis", _raise_error)

    response = client.post("/analyze", json={"query": "analyze"})

    assert response.status_code == 500
    assert response.json() == {"detail": "analyze-boom"}


def test_report_happy_path() -> None:
    response = client.post(
        "/report",
        json={"query": "generate report for lido", "protocol": "lido"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert payload["data"]["agent"] == "report"
    assert "report" in payload["data"]


def test_report_error_path_internal_error(monkeypatch) -> None:
    def _raise_error(*_args, **_kwargs):
        raise RuntimeError("report-boom")

    monkeypatch.setattr(report_route.orchestrator, "run_report", _raise_error)

    response = client.post("/report", json={"query": "report"})

    assert response.status_code == 500
    assert response.json() == {"detail": "report-boom"}


def test_payload_validation_error_for_empty_query() -> None:
    endpoints = ["/chat", "/analyze", "/report"]

    for endpoint in endpoints:
        response = client.post(endpoint, json={"query": ""})
        assert response.status_code == 422
