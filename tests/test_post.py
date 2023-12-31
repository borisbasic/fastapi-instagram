from fastapi.testclient import TestClient
from main import app
from database.database import get_db
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

def test_create_post():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    creator_id = response.json()['id']
    username = response.json()['username']
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    
    assert 'access_token' in response.json()

    
    access_token = response.json()['access_token']
    
    response = client.post('/post', 
                           json={'image_url': 'img_1.jpg',
                                          'image_url_type': 'relative',
                                          'caption': 'first_caption',
                                          'creator_id': creator_id},
                                          headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    data = response.json()
    assert data['image_url'] == 'img_1.jpg'
    assert data['image_url_type'] == 'relative'
    assert data['caption'] == 'first_caption'
    assert data['comments'] == []
    assert data['user']['username'] == username



def test_get_all_posts():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    creator_id = response.json()['id']
    username = response.json()['username']
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    
    assert 'access_token' in response.json()

    
    access_token = response.json()['access_token']
    
    response = client.post('/post', 
                           json={'image_url': 'img_1.jpg',
                                          'image_url_type': 'relative',
                                          'caption': 'first_caption',
                                          'creator_id': creator_id},
                                          headers={'Authorization': f'Bearer {access_token}'})

    data = response.json()

    response = client.get('/post/all')
    assert response.status_code == 200
    assert response.json()[0]['image_url'] == 'img_1.jpg'


def test_user_posts():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    creator_id = response.json()['id']
    username = response.json()['username']
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    
    assert 'access_token' in response.json()

    
    access_token = response.json()['access_token']
    
    response = client.post('/post', 
                           json={'image_url': 'img_1.jpg',
                                          'image_url_type': 'relative',
                                          'caption': 'first_caption',
                                          'creator_id': creator_id},
                                          headers={'Authorization': f'Bearer {access_token}'})

    data = response.json()
    user_id = data['user']['id']
    response = client.get(f'/post/user_posts/{user_id}', 
                          headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json()[0]['image_url'] == 'img_1.jpg'


def test_user_post_delete():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    creator_id = response.json()['id']
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    
    assert 'access_token' in response.json()

    
    access_token = response.json()['access_token']
    
    response = client.post('/post', 
                           json={'image_url': 'img_1.jpg',
                                          'image_url_type': 'relative',
                                          'caption': 'first_caption',
                                          'creator_id': creator_id},
                                          headers={'Authorization': f'Bearer {access_token}'})

    data = response.json()
    post_id = data['id']
    response = client.get(f'/post/delete/{post_id}', 
                          headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json() == 'ok'


def test_user_post_delete_not_found_post():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    
    assert 'access_token' in response.json()

    access_token = response.json()['access_token']
    post_id = 0 
    response = client.get(f'/post/delete/{post_id}', 
                          headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 404
    assert response.json()['detail'] == f'Post with id {post_id} not found.'



def test_user_post_delete_different_user():
    response = client.post('/user', json={'username': 'boris',
                                          'email': 'boris@boris.com',
                                          'password': '123'})
    
    response_2 = client.post('/user', json={'username': 'boris_2',
                                          'email': 'boris_2@boris.com',
                                          'password': '123'})
    creator_id = response.json()['id']
    data_ = response.json()
    response = client.post('/login',data={'username': data_['username'],
                                           'password': '123'})
    data_2 = response_2.json()
    response_2 = client.post('/login', data={'username': data_2['username'],
                                             'password': '123'})
    
    access_token = response.json()['access_token']
    access_token_2 = response_2.json()['access_token']
    response = client.post('/post', 
                           json={'image_url': 'img_1.jpg',
                                          'image_url_type': 'relative',
                                          'caption': 'first_caption',
                                          'creator_id': creator_id},
                                          headers={'Authorization': f'Bearer {access_token}'})

    data = response.json()
    post_id = data['id']
    response = client.get(f'/post/delete/{post_id}', 
                          headers={'Authorization': f'Bearer {access_token_2}'})
    assert response.status_code == 403
    assert response.json()['detail'] == 'Only post creator can delete post.'