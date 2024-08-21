import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from common.objects import users
from src.users.interfaces import (
    OAuthSignInRequest, 
    SignInRequest, 
    SignUpRequest,
    LoginResponse
    )
import json
import requests
import os
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


@router.post("/login", response_model=LoginResponse)
def login(request: SignInRequest):
    try:
        access_token = users.login(
            request.email, request.password
        )
        return LoginResponse(access_token=access_token)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/logout")
def logout(request:Request):
    try:
        authorization = request.headers.get("Authorization")
        users.logout(authorization.replace("Bearer ", ""))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/login/oauth")
def oauth_login(code: str, state: str):
    try:
        decoded_state = json.loads(state)
        provider = decoded_state.get('provider')
        redirect_url = decoded_state.get('redirect_url')

        # Step 1: Prepare the token request details
        client_id = "1011738102559-jgqp1op70bit0nlso2jt9o0a4qdqh18s.apps.googleusercontent.com"
        client_secret = "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"
        redirect_uri = "http://localhost:8080/login/oauth"  # This should match the one in your Google console
        token_url = "https://oauth2.googleapis.com/token"

        # Step 2: Prepare the data for the token request
        token_data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        # Step 3: Make the POST request to Google's token endpoint
        token_response = requests.post(token_url, data=token_data)

        # Step 4: Raise an exception if the request failed
        token_response.raise_for_status()
        tokens = token_response.json()
        id_token = tokens['id_token']

        if not id_token:
            raise HTTPException(status_code=400, detail="Failed to obtain ID token from Google")

        # Forward the ID token to Supabase
        supabase_response = requests.post(
            f'{os.getenv("SUPABASE_URL")}/auth/v1/callback',
            headers={
                'apikey': os.getenv("SUPABASE_KEY"),
                'Authorization': f'Bearer {id_token}',
            },
            json={
                'provider': provider,
                'access_token': tokens['access_token'],
            },
        )

        if supabase_response.status_code != 200:
            raise HTTPException(status_code=supabase_response.status_code, detail="Failed to authenticate with Supabase")

        # Return or process the response from Supabase
        print(supabase_response.json())
    #     # Step 5: Parse the tokens from the response
    #     tokens = token_response.json()

    #     if "id_token" not in tokens:
    #         raise HTTPException(status_code=400, detail="Failed to retrieve ID token from Google")

    #     # Extract the tokens
    #     access_token = tokens["access_token"]
    #     id_token = tokens["id_token"]
    #     print(tokens)
    #     oauth_response = users.exchange_code(code)
    #     print(oauth_response)
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

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
