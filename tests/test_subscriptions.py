from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from . import schemas, models, utils
from .database import get_db
from .api.subscriptions import router

client = TestClient(router)

# Mock database session
async def get_db():
    db = Session(bind=engine, expire_on_commit=False)
    try:
        yield db
    finally:
        db.close()

# Mock current user
async def get_current_user(*args, **kwargs):
    return models.User(id=1, username='testuser', email='testuser@example.com', password='testpassword')

# Test get_subscription
async def test_get_subscription(db: Session):
    subscription = models.Subscription(user_id=1, name='Test Subscription', price=100)
    db.add(subscription)
    db.commit()
    response = client.get('/subscriptions/1', headers={'Authorization': 'Bearer testtoken'})
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'name': 'Test Subscription', 'price': 100}

# Test create_subscription
async def test_create_subscription(db: Session):
    response = client.post('/subscriptions', headers={'Authorization': 'Bearer testtoken'}, json={'name': 'New Subscription', 'price': 200})
    assert response.status_code == 201
    assert response.json() == {'id': 2, 'name': 'New Subscription', 'price': 200}
