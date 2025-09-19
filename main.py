from fastapi import FastAPI
import cloudinary
import os
from dotenv import load_dotenv
from routes.users import users_router
from routes.jobs import job_router

# import cloudinary.api

load_dotenv()

# Configure Cloudinary

cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
)

app = FastAPI(title="Welcome to Job Hub")  # These two lines of code creates a server for you.


@app.get("/", tags=['Welcome to the HomePage'])
def get_home():
    return {"message": "You are on the homepage"}

app.include_router(users_router)
app.include_router(job_router)