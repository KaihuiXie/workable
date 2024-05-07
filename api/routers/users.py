import logging

from fastapi import HTTPException, APIRouter
from common.objects import supabase
from src.interfaces import OAuthSignInRequest, SignInRequest, SignUpRequest


router = APIRouter(
    # prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/signup")
async def signup(request: SignUpRequest):
    try:
        auth_response = supabase.sign_up(request.email, request.phone, request.password)
        return {"auth_response": auth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(request: SignInRequest):
    try:
        auth_response = supabase.sign_in_with_password(
            request.email, request.phone, request.password
        )
        user_id = auth_response.user.id
        temp_credit = supabase.get_temp_credit_by_user_id(user_id)
        perm_credit = supabase.get_perm_credit_by_user_id(user_id)
        return {
            "auth_response": auth_response,
            "temp_credit": temp_credit,
            "perm_credit": perm_credit,
        }
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout():
    try:
        auth_response = supabase.sign_out()
        return {"auth_response": auth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/oauth")
async def login_oauth(request: OAuthSignInRequest):
    try:
        oauth_response = supabase.sign_in_with_oauth(request.provider)
        return {
            "oauth_response": oauth_response,
        }
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
