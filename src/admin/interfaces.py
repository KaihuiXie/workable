from pydantic import BaseModel, Field


class InviteByEmailRequest(BaseModel):
    email: str = Field(..., description="User email")
    redirect_to_url: str = Field(..., description="Redirect url")


class InviteByEmailResponse(BaseModel):
    user_id: str = Field(..., description="user_id created.")
