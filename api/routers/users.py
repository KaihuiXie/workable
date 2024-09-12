import logging
import urllib.parse

from fastapi import APIRouter, HTTPException, Request, Form, Header, status
from fastapi.responses import RedirectResponse
from common.objects import users, ems, payment_service, invitations, url_platforms
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
from src.url_platforms.interfaces import (
    IncrementClicksRequest,
    UpdateUserProfilePlatformIdRequest,
)
from src.stripe.interfaces import CheckoutSessionRequest
import json
import urllib
from src.utils import is_valid_jwt_format

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
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
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
        invitation_token = decoded_state.get('invitation_token')
        platform_token = decoded_state.get('platform_token')

        #retreive user tokens from provider
        tokens = users.exchange_code_for_token(code,provider)
        #save info into supabase
        sessions = users.save_oauth_session(tokens["id_token"],provider)
        if invitation_token and not users.supabase.get_invitation_token_from_user_profile(sessions["user"].get("id")):
            users.supabase.set_invitation_token_from_user_profile(sessions["user"].get("id"),invitation_token)
        if platform_token and not users.supabase.get_platform_token_from_user_profile(sessions["user"].get("id")):
            users.supabase.set_platform_id_from_user_profile(sessions["user"].get("id"),platform_token)

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
        invitation_token = decoded_state.get('invitation_token')
        platform_token = decoded_state.get('platform_token')

        #retreive user tokens from provider
        tokens = users.exchange_code_for_token(code,provider)
        #save info into supabase
        sessions = users.save_oauth_session(tokens["id_token"],provider)

        #update platform_id and invitation_token
        if invitation_token:
            users.supabase.set_invitation_token_from_user_profile(sessions["user"].get("id"),invitation_token)
        if platform_token:
            users.supabase.set_platform_id_from_user_profile(sessions["user"].get("id"),platform_token)

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
def get_user_info(request: Request):
    try:
        authorization = request.headers.get('Authorization')
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        response = users.get_user(authorization.replace("Bearer ", ""))
        invitation_token = users.supabase.get_invitation_token_from_user_profile(response.user_id)
        response.is_valid_for_new = invitations.get_invitation_by_token(invitation_token, response.user_id)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset_password")
def reset_password(request: ResetPasswordRequest):
    try:
        response = users.reset_password_email(request.email, request.options.model_dump())
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_password")
def reset_password(request: UpdatePasswordRequest, authorization:str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        user = users.verify_jwt(authorization.replace("Bearer ", ""))
        if not user:
            raise AuthorizationError("Authorization header missing or expired")
        response = users.update_password(request.model_dump(),authorization.replace("Bearer ", ""))
        return response
    except AuthorizationError as e:
        logging.error(e)
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
        logging.error(e)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

@router.post("/sign_up_by_email", response_model=LoginResponse)
def sign_up_by_email(request: SignUpRequest) -> LoginResponse:
    try:
        response = users.sign_up_with_email(request.email, request.password)
        if request.invitation_token:
            response.user_info.is_valid_for_new = invitations.get_invitation_by_token(request.invitation_token, response.user_info.user_id)
        if request.platform_token:
            url_platforms.increment_clicks(IncrementClicksRequest(platform_id=request.platform_token))
            url_platforms.update_platform_id(UpdateUserProfilePlatformIdRequest(platform_id=request.platform_token,user_id=response.user_info.user_id))
        return response
    except HTTPException as e:
        logging.error(e)
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
    await payment_service.process_event(payload, sig_header)
    return {"status": "success"}

@router.get("/user_subscription")
def get_user_subscription(request: Request):
    try:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        try:
            user_id = users.verify_jwt(authorization.replace("Bearer ", "")).user.id
        except Exception as e:
            raise HTTPException(status_code=401, detail=e)
        return {"result":users.get_subscription(user_id)}
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user_subscription/info")
def get_user_subscription_info(request: Request):
    try:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        try:
            user_email = users.verify_jwt(authorization.replace("Bearer ", "")).user.email
        except Exception as e:
            raise HTTPException(status_code=401, detail=e)
        return payment_service.get_customer_info(user_email)
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/create_checkout_session")
async def create_checkout_session(request: CheckoutSessionRequest):
    try:
        return payment_service.create_subscription_session(request.email, request.successUrl, request.cancelUrl, request.priceId)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)