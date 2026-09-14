import json
import uuid
import pytest
from src.api.subscriptions import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json() == {'status': 'ok'}

def test_update_eligibility_success(client):
    coupon_id = uuid.uuid4()
    payload = {
        'min_order_amount': 10.5,
        'product_category': 'electronics',
        'user_segment': 'premium'
    }
    resp = client.patch(f'/coupons/{coupon_id}/eligibility',
                        data=json.dumps(payload),
                        content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['coupon_id'] == str(coupon_id)
    assert data['min_order_amount'] == 10.5
    assert data['product_category'] == 'electronics'
    assert data['user_segment'] == 'premium'

def test_update_eligibility_negative_amount(client):
    coupon_id = uuid.uuid4()
    payload = {'min_order_amount': -5}
    resp = client.patch(f'/coupons/{coupon_id}/eligibility',
                        data=json.dumps(payload),
                        content_type='application/json')
    assert resp.status_code == 400
    assert resp.get_json()['error'] == 'min_order_amount must be non-negative'
