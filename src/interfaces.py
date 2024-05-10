from enum import Enum
from typing import List, Optional

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ValidationError, model_validator


# Define a Pydantic model for the request data
class SignUpRequest(BaseModel):
    email: str
    phone: Optional[str] = None
    password: str


class SignInRequest(BaseModel):
    email: str
    phone: Optional[str] = None
    password: str


class OAuthSignInRequest(BaseModel):
    provider: str


class UpdateCreditRequest(BaseModel):
    user_id: str
    credit: int


class DecrementCreditRequest(BaseModel):
    user_id: str
