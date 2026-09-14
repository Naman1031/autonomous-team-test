import pytest
from fastapi.testclient import TestClient
from src.api.subscriptions import app

client = TestClient(app)

def test_create_coupon_success():
    payload = {
        "code": "WELCOME10",
        "discount_type": "PERCENTAGE",
        "discount_value": 10,
        "min_order_amount": None,
        "expires_at": None
    }
    response = client.post("/api/v1/coupons", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == payload["code"]
    assert data["discount_type"] == payload["discount_type"]
    assert data["discount_value"] == payload["discount_value"]
    assert data["is_active"] is True

def test_create_coupon_duplicate_code():
    payload = {
        "code": "DUPLICATE",
        "discount_type": "FIXED_AMOUNT",
        "discount_value": 5,
        "min_order_amount": None,
        "expires_at": None
    }
    # First creation should succeed
    resp1 = client.post("/api/v1/coupons", json=payload)
    assert resp1.status_code == 201
    # Second creation with same code must fail
    resp2 = client.post("/api/v1/coupons", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Coupon code already exists"
