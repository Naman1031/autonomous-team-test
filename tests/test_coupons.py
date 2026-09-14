import json
import uuid
import pytest
from src.api import create_app

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client

def test_update_eligibility_success(client):
    # First create a coupon
    resp = client.post('/coupons', json={
        'code': 'TEST10',
        'discount_type': 'PERCENT',
        'discount_value': 10
    })
    assert resp.status_code == 201
    coupon_id = resp.get_json()['id']

    # Update eligibility with valid criteria
    resp = client.patch(f'/coupons/{coupon_id}/eligibility', json={
        'min_order_amount': 50,
        'product_category': 'electronics',
        'user_segment': 'new_customers'
    })
    assert resp.status_code == 200
    assert resp.get_json()['message'] == 'Eligibility criteria updated'

def test_update_eligibility_negative_amount(client):
    # Create a coupon
    resp = client.post('/coupons', json={
        'code': 'NEG1',
        'discount_type': 'FIXED',
        'discount_value': 5
    })
    coupon_id = resp.get_json()['id']

    # Attempt to set a negative min_order_amount
    resp = client.patch(f'/coupons/{coupon_id}/eligibility', json={
        'min_order_amount': -10
    })
    assert resp.status_code == 400
    assert 'min_order_amount' in resp.get_json()['error']
