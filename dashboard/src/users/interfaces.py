from typing import Optional
from pydantic import BaseModel

class UserInfo(BaseModel):
    user_id: int
    email: str
    token: str
    name: Optional[str] = None

class LoginResponse(BaseModel):
    user_info: UserInfo

class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str

class SignInRequest(BaseModel):
    name: str
    email: str
    password: str
    