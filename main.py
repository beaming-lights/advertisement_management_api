from fastapi import FastAPI
from bson.objectid import ObjectId
from pydantic import BaseModel
from db import users_collection
from db import jobs_collection
from db import categories_collection
from db import companies_collection
from db import applications_collection

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

