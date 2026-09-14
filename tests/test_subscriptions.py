import pytest
from fastapi.testclient import TestClient
from src.api.subscriptions import app
from datetime import datetime, timedelta

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

def test_set_coupon_expiration_success():
    # Create a coupon first
    create_payload = {
        "code": "EXPIRYTEST",
        "discount_type": "PERCENTAGE",
        "discount_value": 15,
        "min_order_amount": None,
        "expires_at": None
    }
    create_resp = client.post("/api/v1/coupons", json=create_payload)
    assert create_resp.status_code == 201
    coupon = create_resp.json()
    coupon_id = coupon["id"]

    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    patch_resp = client.patch(f"/api/v1/coupons/{coupon_id}/expiration", json={"expires_at": future_date})
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["expires_at"] == future_date

def test_set_coupon_expiration_past_failure():
    # Create a coupon first
    create_payload = {
        "code": "PASTFAIL",
        "discount_type": "FIXED_AMOUNT",
        "discount_value": 20,
        "min_order_amount": None,
        "expires_at": None
    }
    create_resp = client.post("/api/v1/coupons", json=create_payload)
    assert create_resp.status_code == 201
    coupon_id = create_resp.json()["id"]

    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    patch_resp = client.patch(f"/api/v1/coupons/{coupon_id}/expiration", json={"expires_at": past_date})
    assert patch_resp.status_code == 400
    assert patch_resp.json()["detail"] == "invalid date"
