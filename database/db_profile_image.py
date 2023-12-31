from routers.schemas import PostBase
from sqlalchemy.orm.session import Session
from database.models import DbProfileImage
import datetime


def post_profile_image(db: Session, request: PostBase):
    pi = (
        db.query(DbProfileImage)
        .filter(DbProfileImage.user_id == request.user_id)
        .first()
    )
    if pi:
        pi.user_id = request.user_id
        pi.image_url = request.image_url
        pi.timestamp = datetime.datetime.now()
        db.add(pi)
        db.commit()
        db.refresh(pi)
        return pi
    else:
        profile_image = DbProfileImage(
            image_url=request.image_url,
            timestamp=datetime.datetime.now(),
            user_id=request.user_id,
        )
        db.add(profile_image)
        db.commit()
        db.refresh(profile_image)

        return profile_image
