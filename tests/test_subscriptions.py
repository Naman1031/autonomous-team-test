from flask import Flask
import src.api.subscriptions as subs

def test_subscriptions_blueprint():
    """Ensure the subscriptions blueprint registers correctly and returns the expected payload."""
    app = Flask(__name__)
    app.register_blueprint(subs.subscriptions_bp)
    client = app.test_client()
    response = client.get('/subscriptions')
    assert response.status_code == 200
    assert response.get_json() == {"message": "list"}
