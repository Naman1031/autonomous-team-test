from flask import Blueprint, request, jsonify

coupons_bp = Blueprint('coupons', __name__)

# In‑memory store for eligibility criteria (for test purposes only)
_eligibility_store = {}

@coupons_bp.route('/coupons/<uuid:coupon_id>/eligibility', methods=['PATCH'])
def update_eligibility(coupon_id):
    data = request.get_json() or {}
    # Validate min_order_amount if provided
    if 'min_order_amount' in data:
        try:
            amount = float(data['min_order_amount'])
            if amount < 0:
                return {'error': 'min_order_amount must be non-negative'}, 400
        except (ValueError, TypeError):
            return {'error': 'min_order_amount must be a number'}, 400
    # Update eligibility store
    _eligibility_store[str(coupon_id)] = {
        'min_order_amount': data.get('min_order_amount'),
        'product_category': data.get('product_category'),
        'user_segment': data.get('user_segment')
    }
    response = {'coupon_id': str(coupon_id)}
    response.update(_eligibility_store[str(coupon_id)])
    return jsonify(response), 200
