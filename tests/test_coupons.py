import json
import uuid
import pytest
from src.api.coupons import create_app, db, Coupon, CouponEligibility

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client

def test_create_coupon_unique_success(client):
    payload = {
        "code": "WELCOME10",
        "discount_type": "PERCENTAGE",
        "discount_value": 10.0,
        "status": "DRAFT",
        "valid_from": "2025-01-01T00:00:00",
        "valid_to": "2025-12-31T23:59:59"
    }
    # First creation should succeed
    resp = client.post('/coupons', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["message"] == "Coupon created successfully"
    coupon_id = data["coupon"]["id"]

    # Duplicate code should be rejected
    resp_dup = client.post('/coupons', data=json.dumps(payload), content_type='application/json')
    assert resp_dup.status_code == 400
    err = resp_dup.get_json()
    assert err["error"] == "Coupon code already exists"

def test_set_eligibility_success(client):
    # Create a coupon first
    coupon_payload = {
        "code": "SAVE20",
        "discount_type": "FIXED",
        "discount_value": 20.0,
        "status": "DRAFT",
        "valid_from": "2025-01-01T00:00:00",
        "valid_to": "2025-12-31T23:59:59"
    }
    resp = client.post('/coupons', data=json.dumps(coupon_payload), content_type='application/json')
    assert resp.status_code == 201
    coupon_id = resp.get_json()["coupon"]["id"]

    eligibility_payload = {
        "min_order_amount": 50.0,
        "product_category": "Electronics",
        "user_segment": "VIP"
    }
    resp_elig = client.patch(f'/coupons/{coupon_id}/eligibility', data=json.dumps(eligibility_payload), content_type='application/json')
    assert resp_elig.status_code == 200
    data = resp_elig.get_json()
    assert data["message"] == "Eligibility criteria updated successfully"
    assert data["coupon_id"] == coupon_id
    assert data["eligibility"]["min_order_amount"] == 50.0
    assert data["eligibility"]["product_category"] == "Electronics"
    assert data["eligibility"]["user_segment"] == "VIP"

    # Verify persistence
    with client.application.app_context():
        eligibility = CouponEligibility.query.filter_by(coupon_id=uuid.UUID(coupon_id)).first()
        assert eligibility is not None
        assert float(eligibility.min_order_amount) == 50.0
        assert eligibility.product_category == "Electronics"
        assert eligibility.user_segment == "VIP"

def test_set_eligibility_invalid_negative_amount(client):
    # Create a coupon first
    coupon_payload = {
        "code": "NEGTEST",
        "discount_type": "FIXED",
        "discount_value": 5.0,
        "status": "DRAFT",
        "valid_from": "2025-01-01T00:00:00",
        "valid_to": "2025-12-31T23:59:59"
    }
    resp = client.post('/coupons', data=json.dumps(coupon_payload), content_type='application/json')
    assert resp.status_code == 201
    coupon_id = resp.get_json()["coupon"]["id"]

    bad_payload = {"min_order_amount": -10}
    resp_bad = client.patch(f'/coupons/{coupon_id}/eligibility', data=json.dumps(bad_payload), content_type='application/json')
    assert resp_bad.status_code == 400
    err = resp_bad.get_json()
    assert err["error"] == "min_order_amount cannot be negative"
