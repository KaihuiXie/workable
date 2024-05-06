from enum import Enum
from fastapi import UploadFile, Form, HTTPException, File
from pydantic import BaseModel, model_validator, ValidationError
from typing import Optional, List


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
