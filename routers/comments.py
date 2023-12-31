from fastapi import APIRouter
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_comment
from fastapi import Depends
from routers.schemas import CommentBase, UserAuth, CommentUpdate
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/comment",
    tags=["comment"],
)


@router.get("/all/{post_id}")
def comments(post_id: int, db: Session = Depends(get_db)):
    return db_comment.get_all(db, post_id)


@router.post("")
def create(
    request: CommentBase,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db_comment.create(db, request)


@router.delete("")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db_comment.delete_comment(db, current_user.username, comment_id)


@router.put("")
def update_comment(
    request: CommentUpdate,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db_comment.update_comment(request, db, current_user.username, comment_id)
