from routers.schemas import PostBase
from sqlalchemy.orm.session import Session
from database.models import DbPost
import datetime
from fastapi import HTTPException, status


def create(db: Session, request: PostBase):
    new_post = DbPost(
        image_url=request.image_url,
        image_url_type=request.image_url_type,
        caption=request.caption,
        timestamp=datetime.datetime.now(),
        user_id=request.creator_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_all(db: Session):
    return db.query(DbPost).all()


def delete(db: Session, id: int, user_id):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found.",
        )
    print(user_id.id)
    print(f"post_user_id {post.user_id}")
    if post.user_id != user_id.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only post creator can delete post.",
        )
    db.delete(post)
    db.commit()
    return "ok"


def get_user_posts(db: Session, user_id: int):
    posts = db.query(DbPost).filter(DbPost.user_id == user_id).all()
    return posts


def get_other_posts(db: Session, user_id: int):
    posts = db.query(DbPost).all()
    posts_other = []
    for p in posts:
        if p.user_id != user_id:
            posts_other.append(p)
    return posts_other
