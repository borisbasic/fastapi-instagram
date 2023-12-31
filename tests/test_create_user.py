from fastapi.testclient import TestClient
from main import app
from database.database import get_db
from .override_get_db import override_get_db

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
