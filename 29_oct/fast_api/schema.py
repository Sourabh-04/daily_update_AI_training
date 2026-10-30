
from pydantic import BaseModel, EmailStr, Field


class CandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
