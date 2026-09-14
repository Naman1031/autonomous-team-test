from flask import Flask, Blueprint, request, jsonify
import uuid, datetime

app = Flask(__name__)
api = Blueprint('api', __name__)

# In‑memory storage to simulate the database
coupons = {}
eligibility = {}

@api.route('/coupons/<uuid:coupon_id>/eligibility', methods=['PATCH'])
def update_eligibility(coupon_id):
    """Define or update eligibility criteria for a coupon.
    Expected JSON body may contain:
      - min_order_amount (numeric, must be >= 0)
      - product_category (string)
      - user_segment (string)
    """
    cid = str(coupon_id)
    if cid not in coupons:
        return jsonify({"error": "Coupon not found"}), 404
    data = request.get_json() or {}
    # Validate min_order_amount if supplied
    if 'min_order_amount' in data:
        try:
            min_amount = float(data['min_order_amount'])
        except (TypeError, ValueError):
            return jsonify({"error": "min_order_amount must be a number"}), 400
        if min_amount < 0:
            return jsonify({"error": "min_order_amount cannot be negative"}), 400
        data['min_order_amount'] = min_amount
    # Update the eligibility record
    record = eligibility.get(cid, {})
    for field in ['min_order_amount', 'product_category', 'user_segment']:
        if field in data:
            record[field] = data[field]
    eligibility[cid] = record
    return jsonify({"coupon_id": cid, "eligibility": record}), 200

@api.route('/coupons', methods=['POST'])
def create_coupon():
    """Create a coupon – helper endpoint used by tests."""
    data = request.get_json() or {}
    coupon_id = uuid.uuid4()
    coupon = {
        "id": str(coupon_id),
        "code": data.get("code", f"CODE-{coupon_id.hex[:6]}"),
        "discount_type": data.get("discount_type", "FIXED"),
        "discount_value": float(data.get("discount_value", 0)),
        "status": "DRAFT",
        "valid_from": data.get("valid_from", datetime.datetime.utcnow().isoformat()),
        "valid_to": data.get("valid_to", (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat()),
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    coupons[str(coupon_id)] = coupon
    return jsonify(coupon), 201

app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)
