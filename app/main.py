from fastapi import FastAPI
from bson.objectid import ObjectId
from pydantic import BaseModel

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
    owner_id: ObjectId("Users._id")

class Jobs(BaseModel):
    title: str
    description: str
    category: str
    employment_type: str
    location: str
    salary_min: int
    salary_max: int
    currency: str
    company_id: ObjectId("Companies.__id")
    posted_by: ObjectId("Users.__id")
    date_posted: str
    application_deadline: str
    status: str

class Applications(BaseModel):
    job_id: ObjectId("Jobs._id")
    applicant_id: ObjectId("User._id")
    cover_letter: str
    resume_url: str
    date_applied: str
    status: str

@app.get("/")
def read_root():
    return {"message": "This is the homepage"}

