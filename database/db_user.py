from routers.schemas import UserBase, UserDisplay
from sqlalchemy.orm.session import Session
from .models import DbUser
from database.hashing import Hash
from fastapi import HTTPException, status


def create_user(db: Session, request: UserBase):
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def show_user(db: Session, id):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    print(user)
    print(user.profile_image)
    print("Proslo")
    return user


def get_user_by_username(db: Session, username: str):
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Username with username {username} not founr!",
        )
    return user
