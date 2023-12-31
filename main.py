from fastapi import FastAPI
from database import models
from database.database import engine
from routers import user
from routers import post
from routers import comments
from fastapi.staticfiles import StaticFiles
from routers import profile_image
from auth import authentication
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(user.router)
app.include_router(post.router)
app.include_router(authentication.router)
app.include_router(comments.router)
app.include_router(profile_image.router)


origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(engine)

app.mount("/images", StaticFiles(directory="images"), name="images")
