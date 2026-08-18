from fastapi.testclient import TestClient

from app.server import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_websocket_endpoint() -> None:
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hello")
        first = websocket.receive_text()
        assert "Hello" in first

        websocket.send_text("interrupt")
        second = websocket.receive_text()
        assert "interrupt" in second.lower()
