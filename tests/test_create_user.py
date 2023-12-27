from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = 'sqlite://'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'boris'
    assert data['email'] == 'boris@boris.com'
    assert 'id' in data

    user_id = data['id']

    response = client.get(f'user/{user_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'boris'
    assert data['email'] == 'boris@boris.com'
