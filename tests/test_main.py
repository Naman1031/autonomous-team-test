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

def test_redirect_existing_short_code():
    shorten_res = client.post("/api/v1/shorten", json={"url": "https://example.com/redirect-target"})
    short_code = shorten_res.json()["short_code"]
    
    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/redirect-target"

def test_redirect_nonexistent_short_code():
    response = client.get("/nonexistent123")
    assert response.status_code == 404
    assert response.json() == {"detail": "Short code not found"}
