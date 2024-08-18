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

# TODO
# @router.post("/signup")
# async def signup(request: SignUpRequest):
#     try:
#         auth_response = await users.signup(
#             request.email, request.phone, request.password
#         )
#         return {"auth_response": auth_response}
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# TODO
# @router.post("/login")
# async def login(request: SignInRequest):
#     try:
#         auth_response, temp_credit, perm_credit = await users.login(
#             request.email, request.phone, request.password
#         )
#         return {
#             "auth_response": auth_response,
#             "temp_credit": temp_credit,
#             "perm_credit": perm_credit,
#         }
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# TODO
# @router.post("/logout")
# async def logout():
#     try:
#         auth_response = await users.logout()
#         return {"auth_response": auth_response}
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# TODO
# @router.post("/login/oauth")
# async def oauth_login(request: OAuthSignInRequest):
#     try:
#         oauth_response = await users.oauth_login(request.provider)
#         return {"oauth_response": oauth_response}
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# TODO
# @router.get("/session")
# async def get_session():
#     try:
#         session = await users.get_session()
#         return {"session": session}
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily_bonus/{user_id}")
def verify_daily_bonus(user_id):
    """
    check if the user is eligible for daily_bonus
    - input: \n
      - user_id : `uuid`, Unique uuid of the user.\n
    - return: `bool` \n
    """
    try:
        return users.get_daily_bonus(user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
