from fastapi import APIRouter, Depends, status, UploadFile, File
from routers.schemas import PostBase, PostDisplay
from sqlalchemy.orm.session import Session
from database.database import get_db
from database import db_post
from fastapi.exceptions import HTTPException
from typing import List
import random, string, shutil
from routers.schemas import UserAuth
from auth.oauth2 import get_current_user
from database.db_post import get_user_posts
from database.models import DbPost, DbUser

router = APIRouter(prefix="/post", tags=["post"])

image_url_type = ["absolute", "relative"]


@router.post("", response_model=PostDisplay)
def create(
    request: PostBase,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    if not request.image_url_type in image_url_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Parameter image_url_type can only take values absolute or realtive!",
        )
    return db_post.create(db, request)


@router.get("/all", response_model=List[PostDisplay])
def posts(db: Session = Depends(get_db)):
    return db_post.get_all(db)


@router.post("/image")
def upload_image(
    image: UploadFile = File(...), current_user: UserAuth = Depends(get_current_user)
):
    letter = string.ascii_letters
    rand_str = "".join(random.choice(letter) for i in range(6))
    new = f"_{rand_str}."
    filename = new.join(image.filename.rsplit(".", 1))
    path = f"images/{filename}"
    with open(path, "w+b") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return {"filename": path}


@router.get("/delete/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db_post.delete(db, id, current_user)


@router.get("/user_posts/{id}", response_model=List[PostDisplay])
def get(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return get_user_posts(db, id)


@router.get("/other_posts", response_model=List[PostDisplay])
def get(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db_post.get_other_posts(db, id)


@router.get("/user_post/{user_id}/{post_id}", response_model=PostDisplay)
def get(
    user_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    post = (
        db.query(DbPost)
        .filter(DbPost.id == post_id and DbPost.user_id == user_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} and {user_id} not found",
        )

    return post
