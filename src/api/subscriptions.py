from flask import Blueprint, jsonify

# Blueprint for subscription related routes
subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('/subscriptions', methods=['GET'])
def list_subscriptions():
    """Return a simple placeholder list of subscriptions.
    In a real system this would query a database or another service.
    """
    return jsonify({"message": "list"}), 200
