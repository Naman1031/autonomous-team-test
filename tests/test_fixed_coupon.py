import pytest
from fastapi.testclient import TestClient
from src.main import app, coupons_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    coupons_db.clear()
    yield
    coupons_db.clear()

def test_create_fixed_coupon_success():
    response = client.post(
        "/api/v1/admin/coupons/fixed",
        json={"code": "FLAT50", "amount": 50.00}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "FLAT50"
    assert data["discount_type"] == "FIXED_AMOUNT"
    assert data["discount_value"] == 50.00
    assert "id" in data

def test_create_fixed_coupon_zero_amount():
    response = client.post(
        "/api/v1/admin/coupons/fixed",
        json={"code": "FREE0", "amount": 0.00}
    )
    assert response.status_code == 400
    assert "greater than zero" in response.json()["detail"]

def test_create_fixed_coupon_negative_amount():
    response = client.post(
        "/api/v1/admin/coupons/fixed",
        json={"code": "INVALID", "amount": -10.00}
    )
    assert response.status_code == 400
    assert "greater than zero" in response.json()["detail"]

def test_create_duplicate_coupon_code():
    client.post(
        "/api/v1/admin/coupons/fixed",
        json={"code": "FLAT50", "amount": 50.00}
    )
    response = client.post(
        "/api/v1/admin/coupons/fixed",
        json={"code": "FLAT50", "amount": 20.00}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
