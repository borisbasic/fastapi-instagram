from fastapi.testclient import TestClient
from main import app
from database.database import get_db
from .override_get_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_login():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    
    assert 'access_token' in response.json()

    


def test_invalid_credentials():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    data_ = response.json()
    response = client.post('/login',data={'username': 'borisboris',
                                           'password': '123'})
    assert response.json()['detail'] == 'Invalid credentials'

def test_incorrect_password():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '1234'})
    assert response.json()['detail'] == 'Incorrect password!'