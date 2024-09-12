import logging

from fastapi import APIRouter, HTTPException

from common.objects import invitations
from src.invitations.interfaces import (
    InvitationTokenResponse,
    UpdateInvitationNotificationRequest,
    VerifyUserIsEligibleForBonus,
)
import uuid
router = APIRouter(
    prefix="/invitation",
    tags=["invitations"],
    responses={404: {"description": "Not found"}},
)
logging.basicConfig(level=logging.INFO)


def is_valid_uuid(user_id):
    try:
        uuid_obj = uuid.UUID(user_id, version=4)
        return str(uuid_obj) == user_id
    except ValueError:
        return False

@router.get("/{user_id}")
def get_invitation_by_user_id(user_id: str) -> InvitationTokenResponse:
    """
    get invitation token of user
    - user_id: `uuid`, Unique uuid of the user.\n
    - return: param response including one field,\n
      - `token`: the invitation token\n
    """
    try:
        if not is_valid_uuid(user_id):
            raise HTTPException(status_code=401, detail="Authorization header missing")
        response = invitations.get_invitation_by_user_id(user_id)
        return InvitationTokenResponse(token=response)
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify_user")
def verify_user(request: VerifyUserIsEligibleForBonus) -> bool:
    """
    verify if the user if valid to get bonus
    - input: param request including two fields,\n
      - user_id : `uuid`, Unique uuid of the user.\n
      - invitation_token : `uuid`, invitation token. \n
    - return: `uuid`, if the user is valid to get welcome bonus\n
    """
    try:
        return invitations.get_invitation_by_token(
            request.invitation_token, request.user_id,
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{user_id}")
def get_referee_list(user_id: str):
    """
    get referee list of the user
    - input: \n
      - user_id : `uuid`, Unique uuid of the user.\n
    - return: `list`, the list of referee information\n
    """
    try:
        if not is_valid_uuid(user_id):
            return []
        return invitations.get_referee_list(user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/is_notified")
def update_isNotified(request: UpdateInvitationNotificationRequest) -> bool:
    """
    update if the user is notified
    - input: \n
      - user_id : `uuid`, Unique uuid of the user.\n
    - return: `bool` \n
    """
    try:
        return invitations.update_notification(request.user_id, request.guest_email)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
