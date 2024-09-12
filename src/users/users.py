import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.users.supabase import UsersSupabase
from fastapi import HTTPException, status
from src.users.interfaces import (
    LoginResponse,
    UserInfo
)
import requests
import os

class User(UsersSupabase):
    def __init__(self, supabase):
        self.supabase: UsersSupabase = supabase

    def signup(self, email, phone, password):
        return self.supabase.sign_up(email, phone, password)

    def login(self, email, password):
        auth_response = self.supabase.sign_in_with_password(email, password)
        package = self.supabase.get_subscription(auth_response.user.id)
        user_info = UserInfo(
            user_id = auth_response.user.id,
            email = auth_response.user.email,
            name = auth_response.user.user_metadata.get("full_name"),
            package = "free" if not package else "premium",
            avatar_url = auth_response.user.user_metadata.get("avatar_url")
        )
        return LoginResponse(
            access_token = auth_response.session.access_token,
            user_info = user_info,
            expires_in = auth_response.session.expires_in,
            expires_at = auth_response.session.expires_at,
            refresh_token = auth_response.session.refresh_token,
            token_type = auth_response.session.token_type
        )

    def logout(self, jwt):
        self.supabase.sign_out(jwt)

    def exchange_code_for_token(self, code:str, provider:str)->dict:
        try:
            base_url = os.getenv("BASE_URL")
            redirect_uri = f"{base_url}/login/callback" 
            if provider=="google":
                token_url = os.getenv("GOOGLE_TOKEN_URL")
                client_id = os.getenv("GOOGLE_CLIENT_ID")
                client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            elif provider=="apple":
                token_url = os.getenv("APPLE_TOKEN_URL")
                client_id = os.getenv("APPLE_CLIENT_ID")
                client_secret = os.getenv("APPLE_CLIENT_SECRET")
            else:
                raise HTTPException(status_code=500, detail="Unsupport provider")
            
            token_data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            return tokens
        except Exception as e:
            logging.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    def save_oauth_session(self, id_token:str, provider:str) -> dict:
        try:
            if not id_token:
                raise HTTPException(status_code=400, detail="Failed to obtain ID token from Google")
            supabase_response = requests.post(
                f'{os.getenv("SUPABASE_URL")}/auth/v1/token?grant_type=id_token',
                headers={
                    'apikey': os.getenv("SUPABASE_KEY"),
                    "Content-Type": "application/json",
                },
                json={
                    'provider': provider,
                    "id_token": id_token
                },
            )
            if supabase_response.status_code != 200:
                raise HTTPException(status_code=supabase_response.status_code, detail="Failed to authenticate with Supabase")
            return supabase_response.json()
        except Exception as e:
            logging.error(e)
            raise HTTPException(status_code=500, detail=str(e))
           
    def get_user(self,jwt):
        response = self.supabase.get_user(jwt)
        package = self.supabase.get_subscription(response.user.id)
        user_info = UserInfo(
            user_id = response.user.id,
            email = response.user.email,
            name = response.user.user_metadata.get("full_name", ""),
            package = "free" if not package else "premium",
            avatar_url = response.user.user_metadata.get("avatar_url", "")
        )
        return user_info

    def reset_password_email(self, email:str, options:dict):
        return self.supabase.reset_password_email(email, options)

    def update_password(self, password:dict, authorization:str):
        return self.supabase.update_password(password,authorization)

    def get_daily_bonus(self, user_id):
        return self.supabase.grant_login_award(user_id)
    
    def sign_up_with_email(self, email, password):
        try:
            auth_response = self.supabase.sign_up_with_email(email, password)
            package = self.supabase.get_subscription(auth_response.user.id)
            user_info = UserInfo(
                user_id = auth_response.user.id,
                email = auth_response.user.user_metadata.get("email"),
                name = auth_response.user.user_metadata.get("full_name"),
                package = "free" if not package else "premium",
                avatar_url = auth_response.user.user_metadata.get("avatar_url")
            )
            return LoginResponse(
                access_token = auth_response.session.access_token,
                user_info = user_info,
                expires_in = auth_response.session.expires_in,
                expires_at = auth_response.session.expires_at,
                refresh_token = auth_response.session.refresh_token,
                token_type = auth_response.session.token_type
            )
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    def verify_jwt(self,jwt):
        try:
            return self.supabase.get_user(jwt)
        except Exception as e:
            raise Exception(f"An error occurred during verify_jwt: {e}")
    
    def verify_email(self,email):
        try:
            return self.supabase.verify_if_user_exist(email)
        except Exception as e:
            raise Exception(f"An error occurred during verify_email: {e}")
    
    def get_subscription(self, user_id):
        try:
            return self.supabase.get_subscription(user_id)
        except Exception as e:
            raise Exception(f"An error occurred during get subscription: {e}")
    # def invite_user_by_email(self, email: str, redirect_to_url: str, invitation_token: str, platform_token: str):
    #     return super().invite_user_by_email(email, redirect_to_url, invitation_token, platform_token)
    
    # def delete_user_by_email(self, email: str):
    #     return super().delete_user_by_email(email)