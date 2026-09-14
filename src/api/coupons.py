import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In‑memory DB for simplicity in tests
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class CouponEligibility(db.Model):
    __tablename__ = 'coupon_eligibility'
    coupon_id = db.Column(UUID(as_uuid=True), db.ForeignKey('coupons.id', ondelete='CASCADE'), primary_key=True)
    min_order_amount = db.Column(db.Numeric(10, 2), nullable=True)
    product_category = db.Column(db.String(50), nullable=True)
    user_segment = db.Column(db.String(50), nullable=True)

    coupon = db.relationship('Coupon', backref=db.backref('eligibility', uselist=False))

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _coupon_to_dict(coupon):
    return {
        "id": str(coupon.id),
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": float(coupon.discount_value),
        "status": coupon.status,
        "valid_from": coupon.valid_from.isoformat(),
        "valid_to": coupon.valid_to.isoformat(),
        "created_at": coupon.created_at.isoformat()
    }

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.route('/coupons', methods=['POST'])
def create_coupon():
    data = request.get_json()
    required_fields = ['code', 'discount_type', 'discount_value', 'status', 'valid_from', 'valid_to']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Enforce uniqueness of coupon code
    existing = Coupon.query.filter_by(code=data['code']).first()
    if existing:
        return jsonify({"error": "Coupon code already exists"}), 400

    try:
        coupon = Coupon(
            code=data['code'],
            discount_type=data['discount_type'],
            discount_value=data['discount_value'],
            status=data['status'],
            valid_from=data['valid_from'],
            valid_to=data['valid_to']
        )
        db.session.add(coupon)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Coupon created successfully", "coupon": _coupon_to_dict(coupon)}), 201

@app.route('/coupons/<uuid:coupon_id>/eligibility', methods=['PATCH'])
def set_eligibility(coupon_id):
    data = request.get_json() or {}
    # Validate criteria – only simple validation required for this story
    if 'min_order_amount' in data:
        try:
            amount = float(data['min_order_amount'])
            if amount < 0:
                return jsonify({"error": "min_order_amount cannot be negative"}), 400
        except ValueError:
            return jsonify({"error": "min_order_amount must be a number"}), 400

    coupon = Coupon.query.get_or_404(coupon_id)
    eligibility = CouponEligibility.query.filter_by(coupon_id=coupon.id).first()
    if not eligibility:
        eligibility = CouponEligibility(coupon_id=coupon.id)
        db.session.add(eligibility)

    # Update fields if they are present in the payload
    if 'min_order_amount' in data:
        eligibility.min_order_amount = data['min_order_amount']
    if 'product_category' in data:
        eligibility.product_category = data['product_category']
    if 'user_segment' in data:
        eligibility.user_segment = data['user_segment']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    response = {
        "message": "Eligibility criteria updated successfully",
        "coupon_id": str(coupon.id),
        "eligibility": {
            "min_order_amount": float(eligibility.min_order_amount) if eligibility.min_order_amount is not None else None,
            "product_category": eligibility.product_category,
            "user_segment": eligibility.user_segment
        }
    }
    return jsonify(response), 200

# ---------------------------------------------------------------------------
# Application entry point (used by tests)
# ---------------------------------------------------------------------------

def create_app():
    db.create_all()
    return app

if __name__ == '__main__':
    create_app().run(debug=True)