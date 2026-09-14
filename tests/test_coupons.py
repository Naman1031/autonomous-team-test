import pytest
from fastapi.testclient import TestClient
from src.app import app, coupons_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    coupons_db.clear()
    yield
    coupons_db.clear()

def test_create_percentage_coupon_success():
    payload = {"code": "SUMMER10", "percentage": 10.0}
    response = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["coupon"]["code"] == "SUMMER10"
    assert data["coupon"]["discount_type"] == "PERCENTAGE"
    assert data["coupon"]["discount_value"] == 10.0
    assert data["coupon"]["status"] == "ACTIVE"

def test_create_percentage_coupon_min_boundary():
    payload = {"code": "MIN1", "percentage": 1.0}
    response = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert response.status_code == 201
    assert response.json()["coupon"]["discount_value"] == 1.0

def test_create_percentage_coupon_max_boundary():
    payload = {"code": "MAX100", "percentage": 100.0}
    response = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert response.status_code == 201
    assert response.json()["coupon"]["discount_value"] == 100.0

def test_create_percentage_coupon_invalid_under_min():
    payload = {"code": "LOW0", "percentage": 0.0}
    response = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert response.status_code in (400, 422)

def test_create_percentage_coupon_invalid_over_max():
    payload = {"code": "HIGH101", "percentage": 100.1}
    response = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert response.status_code in (400, 422)

def test_create_duplicate_coupon():
    payload = {"code": "SUMMER10", "percentage": 10.0}
    res1 = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert res1.status_code == 201
    res2 = client.post("/api/v1/admin/coupons/percentage", json=payload)
    assert res2.status_code == 400
