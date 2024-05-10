import logging

from fastapi import APIRouter, HTTPException

from common.objects import users
from src.users.interfaces import OAuthSignInRequest, SignInRequest, SignUpRequest

router = APIRouter(
    # prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/signup")
async def signup(request: SignUpRequest):
    try:
        auth_response = await users.signup(
            request.email, request.phone, request.password
        )
        return {"auth_response": auth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(request: SignInRequest):
    try:
        auth_response, temp_credit, perm_credit = await users.login(
            request.email, request.phone, request.password
        )
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
        auth_response = await users.logout()
        return {"auth_response": auth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/oauth")
async def oauth_login(request: OAuthSignInRequest):
    try:
        oauth_response = await users.oauth_login(request.provider)
        return {"oauth_response": oauth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
