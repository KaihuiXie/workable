from typing import Optional
from pydantic import BaseModel
from pydantic import BaseModel, Field

# Define a Pydantic model for the request data
class SignUpRequest(BaseModel):
    email: str
    phone: Optional[str] = None
    password: str


class SignInRequest(BaseModel):
    email: str
    password: str

class SignUpRequest(BaseModel):
    email: str
    password: str
    invitation_token: Optional[str] = None
    platform_token: Optional[str] = None

class UserInfo(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    package: str
    avatar_url: Optional[str] = None
    is_valid_for_new: Optional[bool] = False

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: int
    token_type: str
    user_info: UserInfo

class OAuthSignInRequest(BaseModel):
    provider: str

class ResetPasswordOptions(BaseModel):
    redirect_to:str

class ResetPasswordRequest(BaseModel):
    email: str
    options: ResetPasswordOptions

class UpdatePasswordRequest(BaseModel):
    password: str

class AuthorizationError(Exception):
    """Custom exception for authorization errors. usually happens when frontend doesn't send authorization header"""

    def __init__(self, message):
        super().__init__(message)

class InviteByEmailRequest(BaseModel):
    email: str = Field(..., description="User email")
    redirect_to_url: str = Field(..., description="Redirect url")
    invitation_token: Optional[str] = Field(..., description="invitation_token")
    platform_token: Optional[str] = Field(..., description="platform_token")


class DeleteByEmailRequest(BaseModel):
    email: str = Field(..., description="User email")

class DeleteByEmailResponse(BaseModel):
    result: bool = Field(..., description="result")