from fastapi import Form, File, UploadFile, HTTPException, status, APIRouter, Depends
from bson.objectid import ObjectId
from utils import replace_mongo_id, genai_client
from typing import Annotated
import cloudinary
import cloudinary.uploader
from db import jobs_collection
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles
# from utils import huggingface_client
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.genai import types

load_dotenv()

job_router = APIRouter()


# End Points
@job_router.post(
    "/jobs",
    tags=["Add a Job"],
    dependencies=[Depends(has_roles(["admin", "employer"]))],
)
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
    user_id: Annotated[str, Depends(is_authenticated)],
    flyer: Annotated[bytes, File()]=None,
):
    # if not job_description:
    #     genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    #     model = genai.GenerativeModel(model_name='gemini-2.5-flash')
    #     response = model.generate_content(f"{job_title} job description")
    #     job_description = response.text
    
    job_count = jobs_collection.count_documents(
        filter={"$and": [{"title": job_title}, {"owner": user_id}]}
    )
    if job_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job with {job_title} and {user_id} already exist!",
        )
    if not flyer:
        # Generate AI image with Google Gemini
        response = genai_client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=job_title,
            config=types.GenerateImagesConfig(number_of_images=1)
        )
        flyer = response.generated_images[0].image.image_bytes

    """Inserts a job opportunity"""
    upload_result = cloudinary.uploader.upload(flyer)
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
            "owner": user_id,
        }
    )
    return {"message": "Job listing added successfully"}


# @job_router.get("/jobs", tags=["Get All Jobs"])
# def get_jobs():
#     all_jobs = jobs_collection.find().to_list()
#     return {"data": list(map(replace_mongo_id, all_jobs))}

@job_router.get("/jobs", tags=["Get All Jobs"])
def get_jobs(
    search: str | None = None,
    category: str | None = None,
    location: str | None = None,
    limit: int = 10,
    skip: int = 0,
):
    query_filter = {}
    if search:
        query_filter["$or"] = [
            {"job_title": {"$regex": search, "$options": "i"}},
            {"job_description": {"$regex": search, "$options": "i"}}
        ]

    if category:
        query_filter["category"] = {"$regex": f"^{category}$", "$options": "i"}

    if location:
        query_filter["location"] = {"$regex": f"^{location}$", "$options": "i"}
    
    jobs = list(jobs_collection.find(
        filter=query_filter,
        limit=int(limit),
        skip=int(skip),
    ))

    return {"data": list(map(replace_mongo_id, jobs))}

@job_router.get("/jobs/{job_id}/similar", tags=["Get Similar Jobs"])
def get_similar_events(job_id, limit=10, skip=0):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid mongo id")
    job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    jobs = jobs_collection.find(
        filter={
            "$or": [
                {"job_title": {"$regex": job["job_title"], "$options": "i"}},
                {"job_description": {"$regex": job["job_description"], "$options": "i"}},
            ]
        },
        limit = int(limit),
        skip = int(skip),
    ).to_list()
    return {"data": list(map(replace_mongo_id, jobs))}

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


@job_router.put(
    "/jobs/{job_id}",
    tags=["Edit Job by Id"],
    dependencies=[Depends(has_roles(["admin", "employer"]))],
)
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
    user_id: Annotated[str, Depends(is_authenticated)],
    flyer: Annotated[bytes, File()] = None,
):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    
    if not flyer:
        # Generate AI image Google Image Gen
        response = genai_client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=job_title,
            config=types.GenerateImagesConfig(number_of_images=1)
        )
        flyer = response.generated_images[0].image.image_bytes

    upload_result = cloudinary.uploader.upload(flyer)
    print(upload_result)

    replace_result = jobs_collection.replace_one(
        filter={"_id": ObjectId(job_id), "owner": user_id},
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
            "owner": user_id,
        },
    )
    if not replace_result.modified_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No job found to replace"
        )

    return {"message": "Job replaced successfully"}


@job_router.delete(
    "/jobs/{job_id}",
    tags=["Delete Job by Id"],
    dependencies=[Depends(has_roles(["admin", "employer"]))],
)
def delete_job(job_id, user_id: Annotated[str, Depends(is_authenticated)]):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    # Delete job from database
    delete_result = jobs_collection.delete_one(filter={"_id": ObjectId(job_id), "owner": user_id})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sorry, no job found to delete!")
    # Return response
    return {"message": "Job deleted succesfully."}

@job_router.get("/jobs/users/me", tags=["Employer Dashboard"], dependencies=[Depends(has_roles(["admin", "employer"]))])
def get_my_jobs(user_id: Annotated[str, Depends(is_authenticated)]):
    jobs = jobs_collection.find(filter={"owner": user_id})
    jobs_list = list(jobs)

    return {"data": list(map(replace_mongo_id, jobs_list))}