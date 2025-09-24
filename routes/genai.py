from fastapi import APIRouter, Form, Depends
from typing import Annotated
from dependencies.authn import is_authenticated
from utils import genai_client
# Create genai router

genai_router = APIRouter(tags=["GenAI"], dependencies=[Depends(is_authenticated)])
# Define Endpoint
@genai_router.post("/genai/generate_text")
def generate_text(prompt = Annotated[str, Form()]):
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return {"content": response.text}