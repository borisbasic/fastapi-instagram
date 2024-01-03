from fastapi.testclient import TestClient
from main import app
from database.database import get_db
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)



def test_image(client):
    response = client.post(
        '/user',
        json={'username': 'boris', 'email': 'boris@boris.com', 'password': '123'},
    )

    data = response.json()
    response = client.post(
        'login',
        data={'username': data['username'], 'password': '123'}
    )
    access_token = response.json()['access_token']
    creator_id = response.json()['user_id']
    file_path = '/home/boris/Downloads/profilna_slika.jpg'
    if os.path.isfile(file_path):
        response = client.post('/post/image',
                               files={'image':open(file_path, 'rb')},
                               headers={'Authorization': f'Bearer {access_token}'})
        
        assert response.status_code == 200
        assert 'filename' in response.json()
    filename = response.json()['filename']
    response = client.post(
        '/post',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'image_url': filename, 'image_url_type': 'relative', 'caption': 'first caption', 'creator_id': creator_id}
        )
    assert response.json()['image_url'] == filename