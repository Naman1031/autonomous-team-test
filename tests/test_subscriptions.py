import pytest
from src.api.subscriptions import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_update_eligibility_success(client):
    # Create a coupon first
    resp = client.post('/coupons', json={"code": "TEST10", "discount_type": "FIXED", "discount_value": 10})
    assert resp.status_code == 201
    coupon = resp.get_json()
    coupon_id = coupon['id']

    # Update eligibility criteria
    payload = {"min_order_amount": 50.0, "product_category": "Electronics"}
    resp = client.patch(f'/coupons/{coupon_id}/eligibility', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['eligibility']['min_order_amount'] == 50.0
    assert data['eligibility']['product_category'] == "Electronics"

def test_update_eligibility_negative_amount(client):
    # Create a coupon for the negative‑amount test
    resp = client.post('/coupons', json={"code": "NEG", "discount_type": "FIXED", "discount_value": 5})
    coupon_id = resp.get_json()['id']

    # Attempt to set a negative min_order_amount
    payload = {"min_order_amount": -10}
    resp = client.patch(f'/coupons/{coupon_id}/eligibility', json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "cannot be negative" in data['error']
