from pydantic import BaseModel, Field


class InviteByEmailRequest(BaseModel):
    email: str = Field(..., description="User email")


class InviteByEmailResponse(BaseModel):
    user_id: str = Field(..., description="user_id created.")
