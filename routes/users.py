from fastapi import APIRouter, Form, HTTPException, status
from typing import Annotated
from pydantic import EmailStr
from db import users_collection
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import os

users_router = APIRouter(tags=["User Section"])


@users_router.post("/users/register")
def register_user(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=6)],
):
    # Ensure user does not alreadyb exist
    user_count = users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exist")
    # Hash user password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    # Save user into database
    users_collection.insert_one(
        {"username": username, "email": email, "password": hashed_password}
    )
    # return response
    return {"message": "User registered succesfully"}


@users_router.post("/users/login")
def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
):
    user_in_db = users_collection.find_one(filter={"email": email})
    if not user_in_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email not found")

    hashed_pwd_in_db = user_in_db["password"]

    correct_password = bcrypt.checkpw(password.encode(), hashed_pwd_in_db)

    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password")

    # Generate access token
    encoded_jwt = jwt.encode(
        {
            "id": str(user_in_db["_id"]),
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=7),
        },
        os.getenv("JWT_SECRET_KEY"),
        "HS256",
    )
    return {"message": "User logged in successffully", "access_token": encoded_jwt}