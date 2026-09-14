import uuid
from flask import Blueprint, request, jsonify, current_app

coupons_bp = Blueprint('coupons', __name__)

# In-memory storage for demonstration purposes
# In a real implementation this would be handled by the persistence layer (e.g., SQLAlchemy)
_coupons = {}
_coupon_eligibility = {}

@coupons_bp.route('/coupons/<uuid:coupon_id>/eligibility', methods=['PATCH'])
def update_eligibility(coupon_id):
    if str(coupon_id) not in _coupons:
        return jsonify({'error': 'Coupon not found'}), 404

    data = request.get_json() or {}
    min_order_amount = data.get('min_order_amount')
    product_category = data.get('product_category')
    user_segment = data.get('user_segment')

    # Validation: min_order_amount must be non‑negative if provided
    if min_order_amount is not None:
        try:
            amount = float(min_order_amount)
            if amount < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'error': 'min_order_amount must be a non‑negative number'}), 400

    # Save eligibility criteria
    _coupon_eligibility[str(coupon_id)] = {
        'min_order_amount': min_order_amount,
        'product_category': product_category,
        'user_segment': user_segment
    }

    return jsonify({'message': 'Eligibility criteria updated'}), 200

@coupons_bp.route('/coupons', methods=['POST'])
def create_coupon():
    data = request.get_json() or {}
    coupon_id = uuid.uuid4()
    _coupons[str(coupon_id)] = {
        'code': data.get('code'),
        'discount_type': data.get('discount_type'),
        'discount_value': data.get('discount_value')
    }
    return jsonify({'id': str(coupon_id)}), 201
