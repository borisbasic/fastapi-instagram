from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ImageDisplay(BaseModel):
    image_url:  str

class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserDisplay(BaseModel):
    username: str
    email: str
    profile_image: ImageDisplay | None
    class Config():
        orm_mode = True

class PostBase(BaseModel):
    image_url: str
    image_url_type: str
    caption: str
    creator_id: int


class User(BaseModel):
    username: str

class Comment(BaseModel):
    text: str
    username: str
    timestamp: datetime
    class Config():
        orm_mode = True

class PostDisplay(BaseModel):
    id: int
    image_url: str
    image_url_type: str
    caption: str
    timestamp: datetime
    user: User
    comments: List[Comment]
    class Config():
        orm_mode = True


class UserAuth(BaseModel):
    id: int
    username: str
    email: str

class CommentBase(BaseModel):
    username: str
    text: str
    post_id: int
    user_id: int

class CommentUpdate(BaseModel):
    text: str

class ProfileImage(BaseModel):
    image_url: str
    user_id: int
