from pydantic import BaseModel


class UpdateInvitationNotificationRequest(BaseModel):
    user_id: str
    guest_email: list

class VerifyUserIsEligibleForBonus(BaseModel):
    user_id: str
    invitation_token: str