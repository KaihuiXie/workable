from typing import Optional

from pydantic import BaseModel


# Define a Pydantic model for the request data
class SignUpRequest(BaseModel):
    email: str
    phone: Optional[str] = None
    password: str


class SignInRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str

class OAuthSignInRequest(BaseModel):
    provider: str
