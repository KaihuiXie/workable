from pydantic import BaseModel, Field
from typing import Optional

class InviteByEmailRequest(BaseModel):
    email: str = Field(..., description="User email")
    redirect_to_url: str = Field(..., description="Redirect url")
    invitation_token: Optional[str] = Field(..., description="invitation_token")
    platform_token: Optional[str] = Field(..., description="platform_token")


class InviteByEmailResponse(BaseModel):
    user_id: str = Field(..., description="user_id created.")
