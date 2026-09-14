from flask import Flask, Blueprint

app = Flask(__name__)

# Health check blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health():
    return {'status': 'ok'}

app.register_blueprint(health_bp)

# Import and register coupons blueprint
from .coupons import coupons_bp
app.register_blueprint(coupons_bp)
