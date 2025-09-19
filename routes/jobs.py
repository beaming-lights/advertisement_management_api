from fastapi import Form, File, UploadFile, HTTPException, status, APIRouter, Depends
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
from db import jobs_collection
from dependencies.authn import is_authenticated

job_router = APIRouter()


# End Points
@job_router.post("/jobs", tags=["Add a Job"])
def post_jobs(
    job_title: Annotated[str, Form()],
    company: Annotated[str, Form()],
    job_description: Annotated[str, Form()],
    category: Annotated[str, Form()],
    job_type: Annotated[str, Form()],
    location: Annotated[str, Form()],
    min_salary: Annotated[float, Form()],
    max_salary: Annotated[float, Form()],
    benefits: Annotated[str, Form()],
    requirements: Annotated[str, Form()],
    date_posted: Annotated[str, Form()],
    contact_email: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()],
    user_id: Annotated[str, Depends(is_authenticated)]
):
    job_count = jobs_collection.count_documents(
        filter={"$and": [{"title": job_title}, {"created by": user_id}]}
    )
    if job_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job with {job_title} and {user_id} already exist!",
        )
    """Inserts a job opportunity"""
    upload_result = cloudinary.uploader.upload(flyer.file)
    jobs_collection.insert_one(
        {
            "job_title": job_title,
            "company": company,
            "job_description": job_description,
            "category": category,
            "job_type": job_type,
            "location": location,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "benefits": benefits,
            "requirements": requirements,
            "contact_email": contact_email,
            "date_posted": date_posted,
            "flyer": upload_result["secure_url"],
            "created by": user_id,
        }
    )
    return {"message": "Job listing added successfully"}


@job_router.get("/jobs", tags=["Get All Jobs"])
def get_jobs():
    all_jobs = jobs_collection.find().to_list()
    return {"data": list(map(replace_mongo_id, all_jobs))}


@job_router.get("/jobs/{job_id}", tags=["Get Job by Id"])
def get_jobs_by_id(job_id):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    job = jobs_collection.find_one({"_id": ObjectId(job_id)})

    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")

    return {"data": replace_mongo_id(job)}


@job_router.put("/jobs/{job_id}", tags=["Edit Job by Id"])
def replace_jobs(
    job_id,
    job_title: Annotated[str, Form()],
    company: Annotated[str, Form()],
    job_description: Annotated[str, Form()],
    category: Annotated[str, Form()],
    job_type: Annotated[str, Form()],
    location: Annotated[str, Form()],
    min_salary: Annotated[float, Form()],
    max_salary: Annotated[float, Form()],
    benefits: Annotated[str, Form()],
    requirements: Annotated[str, Form()],
    date_posted: Annotated[str, Form()],
    contact_email: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()],
    user_id: Annotated[str, Depends(is_authenticated)]
):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    upload_result = cloudinary.uploader.upload(flyer.file)
    print(upload_result)

    jobs_collection.replace_one(
        filter={"_id": ObjectId(job_id)},
        replacement={
            "job_title": job_title,
            "company": company,
            "job_description": job_description,
            "category": category,
            "job_type": job_type,
            "location": location,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "benefits": benefits,
            "requirements": requirements,
            "contact_email": contact_email,
            "date_posted": date_posted,
            "flyer": upload_result["secure_url"],
            "replaced by": user_id,
        },
    )
    return {"message": "Job replaced successfully"}


@job_router.delete("/jobs/{job_id}", tags=["Delete Job by Id"])
def delete_job(job_id, user_id: Annotated[str, Depends(is_authenticated)]):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    # Delete job from database
    delete_result = jobs_collection.delete_one(filter={"_id": ObjectId(job_id)})
    if not delete_result.deleted_count:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Sorry, no job found to delete!"
        )
    # Return response
    return {"message": "Job deleted succesfully."}