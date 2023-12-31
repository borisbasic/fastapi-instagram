from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )
    assert response.status_code == 200
