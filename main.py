from fastapi import FastAPI, Form, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
from db import users_collection
from db import jobs_collection
from db import categories_collection
from db import companies_collection
from db import applications_collection
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

app = FastAPI()


class User(BaseModel):
    username: str
    email: str
    password: str
    role: str
    date_joined: str


class Companies(BaseModel):
    name: str
    website: str
    logo_url: str
    description: str
    location: str
    owner_id: str


class Jobs(BaseModel):
    title: str
    description: str
    category: str
    employment_type: str
    location: str
    salary_min: int
    salary_max: int
    currency: str
    company_id: str
    posted_by: str
    date_posted: str
    application_deadline: str
    status: str


class Applications(BaseModel):
    job_id: str
    applicant_id: str
    cover_letter: str
    resume_url: str
    date_applied: str
    status: str


class Categories(BaseModel):
    name: str
    description: str


@app.get("/")
def read_root():
    return {"message": "This is the homepage"}


# End Points
@app.post("/jobs")
def post_jobs(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    category: Annotated[str, Form()],
    employment_type: Annotated[str, Form()],
    location: Annotated[str, Form()],
    salary_min: Annotated[float, Form()],
    salary_max: Annotated[float, Form()],
    currency: Annotated[str, Form()],
    posted_by: Annotated[str, Form()],
    date_posted: Annotated[str, Form()],
    application_deadline: Annotated[str, Form()],
    job_status: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()]
    ):
    """Inserts a job opportunity"""
    upload_result = cloudinary.uploader.upload(flyer.file)
    jobs_collection.insert_one(
        {
            "title": title,
            "description": description,
            "category": category,
            "employment_type": employment_type,
            "location": location,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "currency": currency,
            "posted_by": posted_by,
            "date_posted": date_posted,
            "application_deadline": application_deadline,
            "job_status": job_status,
            "flyer": upload_result["secure_url"]
        }
    )
    return {"message": "Job listing added successfully"}

@app.get("/jobs")
def get_jobs(title="", description="", limit=10, skip=0):
    jobs = jobs_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}},
                {"description": {"$regex": description, "$options": "i"}},
            ]
        },
        limit=int(limit),
        skip=int(skip),
    ).to_list()
    return {"data": list(map(replace_mongo_id, jobs))}

@app.get("/jobs/{job_id}")
def get_jobs_by_id(job_id):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    return {"data": replace_mongo_id(job)}

@app.put("/jobs/{job_id}")
def replace_jobs(
    job_id,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    category: Annotated[str, Form()],
    employment_type: Annotated[str, Form()],
    location: Annotated[str, Form()],
    salary_min: Annotated[float, Form()],
    salary_max: Annotated[float, Form()],
    currency: Annotated[str, Form()],
    posted_by: Annotated[str, Form()],
    date_posted: Annotated[str, Form()],
    application_deadline: Annotated[str, Form()],
    job_status: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()]
):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!")
    upload_result = cloudinary.uploader.upload(flyer.file)
    print(upload_result)

    jobs_collection.replace_one(
        filter={"_id": ObjectId(job_id)},
        replacement=
        {"title": title,
        "description": description,
        "category": category,
        "employment_type": employment_type,
        "location": location,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": currency,
        "posted_by": posted_by,
        "date_posted": date_posted,
        "application_deadline": application_deadline,
        "job_status": job_status,
        "flyer": upload_result["secure_url"]
        }
    )
    return {"message": "Event replaced successfully"}

@app.delete("/jobs/{job_id}")
def delete_job(job_id):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    # Delete event from database
    delete_result = jobs_collection.delete_one(filter={"_id": ObjectId(job_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sorry, no event found to delte!")
    # Return response
    return{"message": "Event deleted succesfully."}