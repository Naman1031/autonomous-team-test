import os
import sys

# Add the path to the src/api package so we can import the FastAPI app defined there
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "api")))

from subscriptions import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_coupon_success():
    payload = {
        "code": "WELCOME10",
        "discount_type": "PERCENTAGE",
        "discount_value": 10,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "usage_limit": 100,
        "active": True
    }
    response = client.post("/coupons", json=payload)
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["message"] == "Coupon created successfully"
    assert json_resp["code"] == "WELCOME10"

def test_create_coupon_duplicate():
    payload = {
        "code": "DUPLICATE",
        "discount_type": "FIXED",
        "discount_value": 5,
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "active": True
    }
    # First creation should succeed
    resp1 = client.post("/coupons", json=payload)
    assert resp1.status_code == 201

    # Second creation with same code should fail
    resp2 = client.post("/coupons", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Coupon code already exists"
