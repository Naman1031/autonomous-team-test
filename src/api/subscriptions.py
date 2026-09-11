import os
from flask import Flask, request
from models import User, Subscription
from services import apply_discount

app = Flask(__name__)

@app.route('/apply-discount', methods=['POST'])
def apply_discount_route():
    user_id = request.json.get('user_id')
    discount = request.json.get('discount')

    user = User.query.get(user_id)
    if user:
        subscription = Subscription.query.filter_by(user_id=user_id).first()
        if subscription:
            apply_discount(subscription, discount)
            return {'message': 'Discount applied successfully'}, 200

    return {'error': 'User or subscription not found'}, 404

if __name__ == '__main__':
    app.run(debug=True)