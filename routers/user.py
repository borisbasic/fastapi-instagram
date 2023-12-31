from fastapi import APIRouter
from routers.schemas import UserDisplay, UserBase
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from database.database import get_db
from database import db_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post("", response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)


@router.get("/{id}", response_model=UserDisplay)
def show_user(id: int, db: Session = Depends(get_db)):
    return db_user.show_user(db, id)
