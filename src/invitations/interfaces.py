from pydantic import BaseModel, Field


class UpdateInvitationNotificationRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user")
    guest_email: list = Field(..., description="The list of the guest_email")


class VerifyUserIsEligibleForBonus(BaseModel):
    user_id: str = Field(..., description="The ID of the user")
    invitation_token: str = Field(..., description="The invitation token of the user")


class InvitationTokenResponse(BaseModel):
    token: str = Field(..., description="The invitation token of the user")


class RefereeEntity(BaseModel):
    guest_email: str = Field(..., description="The guest email of the referee")
    bonus: int = Field(..., description="The bonus of the referee")
    join_date: str = Field(..., description="The join date of the referee")
    referrer_id: str = Field(..., description="The referrer user of the referee")
    isNotify: bool = Field(..., description="if it is notify")


class RefereeListResponse(BaseModel):
    data: list[RefereeEntity] = Field(..., description="The list of the referee")
