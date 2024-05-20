import logging

from fastapi import APIRouter, HTTPException

from common.objects import invitations

router = APIRouter(
    # prefix="/invitations",
    tags=["invitations"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.get("/referrer/{invitation_token}")
async def get_referrer(invitation_token: str):
    try:
        is_invited, referrer_id = invitations.get_referrer(invitation_token)
        return {"is_invited": is_invited, "referrer_id": referrer_id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invitation/{user_id}")
async def get_invitation_by_user_id(user_id: str):
    try:
        response = invitations.get_invitation_by_user_id(user_id)
        return {"token": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invitation/verify_user/{invitation_token}/{user_id}")
async def get_invitation_by_token(invitation_token: str, user_id: str):
    try:
        return invitations.get_invitation_by_token(invitation_token, user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invitation/list/{user_id}")
async def get_referee_list(user_id: str):
    try:
        return invitations.get_referee_list(user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
