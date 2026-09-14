from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime

# Blueprint for coupon related routes
coupons_bp = Blueprint('coupons', __name__)

# In‑memory store for demonstration purposes (replace with DB in production)
_coupons = {}
_coupons_eligibility = {}

@coupons_bp.route('/coupons', methods=['POST'])
def create_coupon():
    """Create a new coupon.
    Expected JSON payload:
    {
        "code": "STRING",
        "discount_type": "PERCENTAGE|FIXED",
        "discount_value": NUMBER,
        "valid_from": "ISO8601 datetime",
        "valid_to": "ISO8601 datetime"
    }
    """
    data = request.get_json() or {}
    required = ["code", "discount_type", "discount_value", "valid_from", "valid_to"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    coupon_id = str(uuid.uuid4())
    coupon = {
        "id": coupon_id,
        "code": data["code"],
        "discount_type": data["discount_type"],
        "discount_value": data["discount_value"],
        "status": "INACTIVE",
        "valid_from": data["valid_from"],
        "valid_to": data["valid_to"],
        "created_at": datetime.utcnow().isoformat()
    }
    _coupons[coupon_id] = coupon
    return jsonify(coupon), 201

@coupons_bp.route('/coupons/<coupon_id>/eligibility', methods=['PATCH'])
def set_eligibility(coupon_id):
    """Define or update eligibility criteria for a coupon.
    Expected JSON payload may include any of:
    {
        "min_order_amount": NUMBER,
        "product_category": "STRING",
        "user_segment": "STRING"
    }
    """
    if coupon_id not in _coupons:
        return jsonify({"error": "Coupon not found"}), 404
    data = request.get_json() or {}
    # Basic validation – reject negative amounts
    if "min_order_amount" in data and data["min_order_amount"] < 0:
        return jsonify({"error": "min_order_amount cannot be negative"}), 400
    # Store/overwrite eligibility criteria
    _coupons_eligibility[coupon_id] = {
        "min_order_amount": data.get("min_order_amount"),
        "product_category": data.get("product_category"),
        "user_segment": data.get("user_segment")
    }
    return jsonify({"coupon_id": coupon_id, "eligibility": _coupons_eligibility[coupon_id]}), 200
