from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shorten_valid_url():
    response = client.post("/api/v1/shorten", json={"url": "https://example.com/long-path"})
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert data["long_url"] == "https://example.com/long-path"

def test_shorten_invalid_url():
    response = client.post("/api/v1/shorten", json={"url": "invalid-url"})
    assert response.status_code == 400
