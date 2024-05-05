import logging

from fastapi import HTTPException, APIRouter
from common.object import supabase

router = APIRouter(
    # prefix="/invitations",
    tags=["invitations"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.get("/referrer/{invitation_token}")
async def get_referrer(invitation_token: str):
    try:
        is_invited, referrer_id = supabase.get_referrer_id_by_invitation_token(
            invitation_token
        )
        return {"is_invited": is_invited, "referrer_id": referrer_id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invitation/{user_id}")
async def get_invitation(user_id: str):
    try:
        response = supabase.get_invitation_by_user_id(user_id)
        return {"token": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invitation/verify_user/{user_email}")
async def get_invitation(user_email: str):
    try:
        response = supabase.if_email_existed(user_email)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))