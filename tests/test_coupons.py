import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.coupons import router
from datetime import datetime, timedelta

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_create_coupon_success():
    payload = {
        "code": "WELCOME10",
        "discount_type": "PERCENT",
        "discount_value": 10,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_to": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    response = client.post("/coupons", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == payload["code"]
    assert data["discount_type"] == payload["discount_type"]
    assert data["discount_value"] == payload["discount_value"]
    assert "id" in data
    assert data["status"] == "CREATED"

def test_create_coupon_missing_field():
    payload = {
        "code": "WELCOME10",
        # missing discount_type
        "discount_value": 10,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_to": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    response = client.post("/coupons", json=payload)
    # FastAPI returns 422 for validation errors
    assert response.status_code == 422

def test_create_coupon_duplicate_code():
    payload = {
        "code": "DUPLICATE",
        "discount_type": "FIXED",
        "discount_value": 5,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_to": (datetime.utcnow() + timedelta(days=10)).isoformat()
    }
    # First creation should succeed
    resp1 = client.post("/coupons", json=payload)
    assert resp1.status_code == 200
    # Second creation with same code should fail
    resp2 = client.post("/coupons", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Coupon code already exists"
