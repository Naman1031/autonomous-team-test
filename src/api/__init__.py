from flask import Flask
from .subscriptions import subscriptions_bp
from .coupons import coupons_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(coupons_bp)
    return app
