from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from src.api.coupons import app, COUPONS_DB

client = TestClient(app)

def setup_function():
    now = datetime.now(timezone.utc)
    COUPONS_DB.clear()
    COUPONS_DB.update({
        "SUMMER10": {"id": "1", "code": "SUMMER10", "discount_type": "PERCENTAGE", "discount_value": 10.0, "max_usages": 100, "current_usages": 0, "starts_at": now - timedelta(days=1), "expires_at": now + timedelta(days=10)},
        "EXPIRED20": {"id": "2", "code": "EXPIRED20", "discount_type": "PERCENTAGE", "discount_value": 20.0, "max_usages": 10, "current_usages": 0, "starts_at": now - timedelta(days=10), "expires_at": now - timedelta(days=1)},
        "MAXEDOUT": {"id": "3", "code": "MAXEDOUT", "discount_type": "FIXED_AMOUNT", "discount_value": 50.0, "max_usages": 5, "current_usages": 5, "starts_at": now - timedelta(days=1), "expires_at": now + timedelta(days=10)}
    })

def test_validate_active_coupon():
    setup_function()
    res = client.post("/api/v1/coupons/validate", json={"code": "SUMMER10"})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["discount_type"] == "PERCENTAGE"
    assert data["discount_value"] == 10.0

def test_validate_nonexistent_coupon():
    setup_function()
    res = client.post("/api/v1/coupons/validate", json={"code": "UNKNOWN"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Coupon code does not exist"

def test_validate_expired_coupon():
    setup_function()
    res = client.post("/api/v1/coupons/validate", json={"code": "EXPIRED20"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Coupon has expired"

def test_validate_fully_redeemed_coupon():
    setup_function()
    res = client.post("/api/v1/coupons/validate", json={"code": "MAXEDOUT"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Coupon usage limit reached"

def test_apply_coupon_percentage():
    setup_function()
    res = client.post("/api/v1/coupons/apply", json={"code": "SUMMER10", "order_subtotal": 100.0})
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == "SUMMER10"
    assert data["original_subtotal"] == 100.0
    assert data["discount_amount"] == 10.0
    assert data["final_subtotal"] == 90.0
