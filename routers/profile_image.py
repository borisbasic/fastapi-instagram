from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm.session import Session
from database.database import get_db
from database import db_profile_image
from fastapi.exceptions import HTTPException
import random, string, shutil
from auth.oauth2 import get_current_user
from routers.schemas import UserAuth, ProfileImage, ImageDisplay

router = APIRouter(prefix="/profile_image", tags=["profile_image"])


@router.post("", response_model=ImageDisplay)
def post_profile_image(
    request: ProfileImage,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db_profile_image.post_profile_image(db, request)


@router.post("/image")
def upload_profile_image(
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
