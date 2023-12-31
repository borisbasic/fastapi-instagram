from fastapi.testclient import TestClient
from main import app
from database.database import get_db
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


def test_post_comment(client):
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )

    response_2 = client.post(
        "/user",
        json={"username": "boris_2", "email": "boris_2@boris.com", "password": "123"},
    )

    data_ = response.json()
    response = client.post(
        "/login", data={"username": data_["username"], "password": "123"}
    )

    data_2 = response_2.json()
    response_2 = client.post(
        "/login", data={"username": data_2["username"], "password": "123"}
    )

    access_token = response.json()["access_token"]
    creator_id = response.json()["user_id"]

    access_token_2 = response_2.json()["access_token"]
    username_2 = response_2.json()["username"]
    response = client.post(
        "/post",
        json={
            "image_url": "img_1.jpg",
            "image_url_type": "relative",
            "caption": "first_caption",
            "creator_id": creator_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    post_id = response.json()["id"]

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    response_post = client.get(
        f"/post/user_post/{creator_id}/{post_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_2.status_code == 200
    assert response_post.status_code == 200
    assert response_post.json()["comments"][0]["text"] == "new comment"
    assert "comments" in response.json()


def test_get_all_comments_for_post(client):
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )

    response_2 = client.post(
        "/user",
        json={"username": "boris_2", "email": "boris_2@boris.com", "password": "123"},
    )

    data_ = response.json()
    response = client.post(
        "/login", data={"username": data_["username"], "password": "123"}
    )

    data_2 = response_2.json()
    response_2 = client.post(
        "/login", data={"username": data_2["username"], "password": "123"}
    )

    access_token = response.json()["access_token"]
    creator_id = response.json()["user_id"]

    access_token_2 = response_2.json()["access_token"]
    username_2 = response_2.json()["username"]
    response = client.post(
        "/post",
        json={
            "image_url": "img_1.jpg",
            "image_url_type": "relative",
            "caption": "first_caption",
            "creator_id": creator_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    post_id = response.json()["id"]

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment 2", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    response_post = client.get(
        f"/comment/all/{post_id}",
    )

    assert response_2.status_code == 200
    assert response_post.status_code == 200
    assert response_post.json()[0]["text"] == "new comment"
    assert response_post.json()[1]["text"] == "new comment 2"
    assert response_post.json()[1]["username"] == username_2


def test_delete_comment(client):
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )

    response_2 = client.post(
        "/user",
        json={"username": "boris_2", "email": "boris_2@boris.com", "password": "123"},
    )

    data_ = response.json()
    response = client.post(
        "/login", data={"username": data_["username"], "password": "123"}
    )

    data_2 = response_2.json()
    response_2 = client.post(
        "/login", data={"username": data_2["username"], "password": "123"}
    )

    access_token = response.json()["access_token"]
    creator_id = response.json()["user_id"]

    access_token_2 = response_2.json()["access_token"]
    username_2 = response_2.json()["username"]
    response = client.post(
        "/post",
        json={
            "image_url": "img_1.jpg",
            "image_url_type": "relative",
            "caption": "first_caption",
            "creator_id": creator_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    post_id = response.json()["id"]

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    comment_id = response_2.json()["id"]

    response_post = client.delete(
        f"/comment?comment_id={comment_id}",
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    assert response_2.status_code == 200
    assert response_post.status_code == 200
    assert response_post.json() == "ok"


def test_delete_comment_error(client):
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )

    response_2 = client.post(
        "/user",
        json={"username": "boris_2", "email": "boris_2@boris.com", "password": "123"},
    )

    data_ = response.json()
    response = client.post(
        "/login", data={"username": data_["username"], "password": "123"}
    )

    data_2 = response_2.json()
    response_2 = client.post(
        "/login", data={"username": data_2["username"], "password": "123"}
    )

    access_token = response.json()["access_token"]
    creator_id = response.json()["user_id"]

    access_token_2 = response_2.json()["access_token"]
    username_2 = response_2.json()["username"]
    response = client.post(
        "/post",
        json={
            "image_url": "img_1.jpg",
            "image_url_type": "relative",
            "caption": "first_caption",
            "creator_id": creator_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    post_id = response.json()["id"]

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    comment_id = response_2.json()["id"]

    response_post = client.delete(
        f"/comment?comment_id={comment_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_2.status_code == 200
    assert response_post.status_code == 403
    assert (
        response_post.json()["detail"] == "Only creator of comment can delete comment!"
    )


def test_update_comment(client):
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )

    response_2 = client.post(
        "/user",
        json={"username": "boris_2", "email": "boris_2@boris.com", "password": "123"},
    )

    data_ = response.json()
    response = client.post(
        "/login", data={"username": data_["username"], "password": "123"}
    )

    data_2 = response_2.json()
    response_2 = client.post(
        "/login", data={"username": data_2["username"], "password": "123"}
    )

    access_token = response.json()["access_token"]
    creator_id = response.json()["user_id"]

    access_token_2 = response_2.json()["access_token"]
    username_2 = response_2.json()["username"]
    response = client.post(
        "/post",
        json={
            "image_url": "img_1.jpg",
            "image_url_type": "relative",
            "caption": "first_caption",
            "creator_id": creator_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    post_id = response.json()["id"]

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    comment_id = response_2.json()["id"]

    response_post = client.put(
        f"/comment?comment_id={comment_id}",
        json={"text": "new change comment"},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    assert response_2.status_code == 200
    assert response_post.status_code == 200
    assert response_post.json() == "ok"


def test_update_comment_error(client):
    response = client.post(
        "/user",
        json={"username": "boris", "email": "boris@boris.com", "password": "123"},
    )

    response_2 = client.post(
        "/user",
        json={"username": "boris_2", "email": "boris_2@boris.com", "password": "123"},
    )

    data_ = response.json()
    response = client.post(
        "/login", data={"username": data_["username"], "password": "123"}
    )

    data_2 = response_2.json()
    response_2 = client.post(
        "/login", data={"username": data_2["username"], "password": "123"}
    )

    access_token = response.json()["access_token"]
    creator_id = response.json()["user_id"]

    access_token_2 = response_2.json()["access_token"]
    username_2 = response_2.json()["username"]
    response = client.post(
        "/post",
        json={
            "image_url": "img_1.jpg",
            "image_url_type": "relative",
            "caption": "first_caption",
            "creator_id": creator_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    post_id = response.json()["id"]

    response_2 = client.post(
        "/comment",
        json={"username": username_2, "text": "new comment", "post_id": post_id},
        headers={"Authorization": f"Bearer {access_token_2}"},
    )

    comment_id = response_2.json()["id"]

    response_post = client.put(
        f"/comment?comment_id={comment_id}",
        json={"text": "new change comment"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_2.status_code == 200
    assert response_post.status_code == 403
    assert (
        response_post.json()["detail"] == "Only creator of comment can delete comment!"
    )
