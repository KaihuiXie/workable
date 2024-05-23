from pydantic import BaseModel


class UpdateInvitationNotificationRequest(BaseModel):
    user_id: str
    guest_email: list
