import logging
import urllib.parse

from fastapi import APIRouter, HTTPException, Request, Form, Header, status
from fastapi.responses import RedirectResponse
from common.objects import users, ems, payment_service
from src.users.interfaces import (
    SignInRequest, 
    LoginResponse,
    UserInfo,
    ResetPasswordRequest,
    AuthorizationError,
    UpdatePasswordRequest,
    InviteByEmailRequest,
    SignUpRequest,
)
import json
import urllib

router = APIRouter(
    # prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)

@router.post("/login", response_model=LoginResponse)
def login(request: SignInRequest):
    try:
        response = users.login(request.email, request.password)
        return response
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

@router.get("/login/callback")
def oauth_callback(code: str, state: str):
    try:
        decoded_state = json.loads(state)
        provider = decoded_state.get('provider')
        redirect_url = decoded_state.get('redirect_url')

        #retreive user tokens from provider
        tokens = users.exchange_code_for_token(code,provider)
        #save info into supabase
        sessions = users.save_oauth_session(tokens["id_token"],provider)

        response_param = {}
        response_param["access_token"] = sessions["access_token"]
        response_param["refresh_token"] = sessions["refresh_token"]
        response_param["expires_in"] = sessions["expires_in"]
        response_param["expires_at"] = sessions["expires_at"]
        response_param["token_type"] = sessions["token_type"]
        redirect_url+=f"?{urllib.parse.urlencode(response_param)}"

        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login/callback")
def oauth_callback(code: str = Form(...), state: str = Form(...)):
    try:
        decoded_state = json.loads(state)
        provider = decoded_state.get('provider')
        redirect_url = decoded_state.get('redirect_url') #frontend location

        #retreive user tokens from provider
        tokens = users.exchange_code_for_token(code,provider)
        #save info into supabase
        sessions = users.save_oauth_session(tokens["id_token"],provider)

        response_param = {}
        response_param["access_token"] = sessions["access_token"]
        response_param["refresh_token"] = sessions["refresh_token"]
        response_param["expires_in"] = sessions["expires_in"]
        response_param["expires_at"] = sessions["expires_at"]
        response_param["token_type"] = sessions["token_type"]

        redirect_url+=f"?{urllib.parse.urlencode(response_param)}"
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/user_info", response_model=UserInfo)
async def get_user_info(request: Request):
    try:
        authorization = request.headers.get('Authorization')
        response = users.get_user(authorization.replace("Bearer ", ""))
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset_password")
async def reset_password(request: ResetPasswordRequest):
    try:
        response = users.reset_password_email(request.email, request.options.model_dump())
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_password")
async def reset_password(request: UpdatePasswordRequest, authorization:str = Header(None)):
    try:
        user = users.verify_jwt(authorization.replace("Bearer ", ""))
        if not user:
            raise AuthorizationError("Authorization header missing or expired")
        response = users.update_password(request.model_dump(),authorization.replace("Bearer ", ""))
        return response
    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invite_user_by_email")
def invite_user_by_email(request: InviteByEmailRequest):
    try:
        if not ems.verify_email(request.email):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="email is invalid")
        if users.verify_email(request.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
        redirect_url = request.redirect_to_url
        response_param = request.model_dump(exclude="redirect_to_url")
        redirect_url+=f"?{urllib.parse.urlencode(response_param)}"
        ems.send_invitation_email(request.email, redirect_url)
        return {"status": "success", "message": "Invitation email sent successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

@router.post("/sign_up_by_email", response_model=LoginResponse)
def sign_up_by_email(request: SignUpRequest) -> LoginResponse:
    try:
        response = users.sign_up_with_email(request.email, request.password)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

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

@router.post("/stripe_webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = payment_service.construct_event(payload, sig_header)

    # Process the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(session)
        # Handle successful payment here

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        print(f"Subscription canceled: {subscription['id']}")
        # Handle subscription cancellation here
        # You can notify the user, update the database, etc.

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        print(f"Payment failed for invoice: {invoice['id']}")
        # Handle payment failure which might lead to subscription cancellation
        # You can notify the user or take other actions

    elif event["type"] == "charge.refunded":
        charge = event["data"]["object"]
        print(f"Charge refunded: {charge['id']}")

    return {"status": "success"}

@router.get("/user_subscription")
def stripe_webhook(user_id, auth):
    return True