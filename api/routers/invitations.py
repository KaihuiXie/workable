import logging

from fastapi import APIRouter, HTTPException

from common.objects import invitations
from src.invitations.interfaces import (
    InvitationTokenResponse,
    RefereeListResponse,
    UpdateInvitationNotificationRequest,
    VerifyUserIsEligibleForBonus,
)

router = APIRouter(
    # prefix="/invitations",
    tags=["invitations"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


# @router.get("/referrer/{invitation_token}")
# async def get_referrer(invitation_token: str):
#     """
#     will be deprecated

#     - invitation_token: `invitation_token` type of string. Unique uuid.\n
#     - return: param response including two fields,\n
#       - `isInvited`: if the token is expired\n
#       - `referrerId`: uuid of the referrer\n
#     """
#     try:
#         is_invited, referrer_id = invitations.get_referrer(invitation_token)
#         return {"is_invited": is_invited, "referrer_id": referrer_id}
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/invitation/{user_id}")
async def get_invitation_by_user_id(user_id: str) -> InvitationTokenResponse:
    """
    get invitation token of user
    - user_id: `uuid`, Unique uuid of the user.\n
    - return: param response including one field,\n
      - `token`: the invitation token\n
    """
    try:
        response = invitations.get_invitation_by_user_id(user_id)
        return InvitationTokenResponse(token=response)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invitation/verify_user")
async def verify_user(request: VerifyUserIsEligibleForBonus) -> bool:
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


@router.get("/invitation/list/{user_id}")
async def get_referee_list(user_id: str) -> RefereeListResponse:
    """
    get referee list of the user
    - input: \n
      - user_id : `uuid`, Unique uuid of the user.\n
    - return: `list`, the list of referee information\n
    """
    try:
        return invitations.get_referee_list(user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/invitation/is_notified/{user_id}")
# async def get_notified(user_id: str) -> bool:
#     """
#     will be deprecated
#     see if the user is notified or not
#     - input: \n
#       - user_id : `uuid`, Unique uuid of the user.\n
#     - return: `bool` \n
#     """
#     try:
#         print(invitations.get_notification_list(user_id))
#         return invitations.get_notification_list(user_id)
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


@router.put("/invitation/is_notified")
async def update_isNotified(request: UpdateInvitationNotificationRequest) -> bool:
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
