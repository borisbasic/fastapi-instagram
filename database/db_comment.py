from sqlalchemy.orm import Session
from database.models import DbComment
from routers.schemas import CommentBase, CommentUpdate
from datetime import datetime
from fastapi import HTTPException, status
def create(db: Session, request: CommentBase):
    new_comment = DbComment(
        text = request.text,
        username = request.username,
        post_id = request.post_id,
        timestamp = datetime.now()
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def get_all(db: Session, post_id: int):
    return db.query(DbComment).filter(DbComment.post_id == post_id).all()

def delete_comment(db: Session, username: str, comment_id: int):
    comment = db.query(DbComment).filter(DbComment.id == comment_id).first()
    if comment.username == username:
        db.delete(comment)
        db.commit()
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only creator of comment can delete comment!')

    return 'ok'

def update_comment(request: CommentUpdate, db: Session, username: str, comment_id: int):
    comment = db.query(DbComment).filter(DbComment.id == comment_id).first()
    print(comment.username)
    print(username)
    if comment.username == username:
        comment.text = request.text
        db.add(comment)
        db.commit()
        db.refresh(comment)
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only creator of comment can delete comment!')

    return 'ok'