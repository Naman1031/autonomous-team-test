import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from . import schemas, models, database
from .auth import get_current_user

@pytest.fixture
async def test_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
async def test_user(test_db: Session) -> models.User:
    db = test_db
    db.add(models.User(id=1, first_name='John', last_name='Doe', email='john.doe@example.com'))
    db.commit()
    db.refresh(db.query(models.User).filter(models.User.id == 1).first())
    return db.query(models.User).filter(models.User.id == 1).first()

@pytest.fixture
async def test_client(test_db: Session) -> TestClient:
    async def override_get_current_user(user_id: int = 1):
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_current_user)


def test_read_user(test_client: TestClient, test_user: models.User):
    response = test_client.get(f'/users/{test_user.id}')
    assert response.status_code == 200
    assert response.json() == schemas.User(id=test_user.id, first_name=test_user.first_name, last_name=test_user.last_name, email=test_user.email)