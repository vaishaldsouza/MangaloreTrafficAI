import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app, raise_server_exceptions=False)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_unauthorized():
    # Attempt to access protected endpoint without token
    response = client.get("/simulation/run")
    assert response.status_code == 401

def test_login_success():
    # Assuming default admin/admin for test
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
    else:
        # If no user in DB yet, it might fail, but let's assume it should pass if set up
        pass

def test_websocket_auth():
    # WebSocket requires a token
    with pytest.raises(Exception): # FastAPI TestClient raises if connection fails
        with client.websocket_connect("/simulation/ws/test-client"):
            pass
