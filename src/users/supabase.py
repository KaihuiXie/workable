from supabase import Client, ClientOptions, create_client
from fastapi import HTTPException, status
from datetime import datetime, timezone
import dateutil.parser
from common.constants import EVERY_DAY_CREDIT_INCREMENT

class UsersSupabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )

    def auth(self):
        return self.auth

    def sign_up_with_email(self, email: str, password: str):
        try:
            # res = self.supabase.auth._request(
            #     "POST",
            #     "signup",
            #     body={
            #         "email": email,
            #         "password": password,
            #         "data": {},
            #     },
            # )
            res =self.supabase.auth.sign_up({
                "email":email,
                "password":password
            })
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing up user with email {email}: {e}"
            )

    def sign_in_with_password(self, email: str, password: str):
        try:
            res = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing in user with email {email}: {e}"
            )

    def sign_in_with_oauth(self, provider: str, token: str):
        try:
            res = self.supabase.auth.sign_in_with_oauth(
                {
                    "provider": provider,
                    "token":token
                }
            )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing in user with oauth provider {provider}: {e}"
            )

    def reset_password_email(self, email, options):
        try:
            return self.supabase.auth.reset_password_email(email, options)
        except Exception as e:
            raise Exception(f"An error occurred during reset password: {e}")

    def update_password(self, password, authorization):
        try:
            return self.supabase.auth._request(
                "PUT",
                "user",
                body=password,
                jwt=authorization
            )
        except Exception as e:
            raise Exception(f"An error occurred during update password: {e}")

    def sign_out(self, jwt):
        try:
            self.supabase.auth._request(
                "POST",
                "logout",
                jwt=jwt,
                no_resolve_json=True,
            )
        except Exception as e:
            raise Exception(f"An error occurred during signing out: {e}")

    def get_user(self,jwt):
        try:
            user_info = self.supabase.auth.get_user(jwt)
            return user_info
        except Exception as e:
            raise Exception(f"An error occurred during getting user info: {e}")

    def invite_user_by_email(self, email: str, redirect_to_url: str, invitation_token:str, platform_token:str):
        try:
            response = self.supabase.auth.admin.invite_user_by_email(
                email, options={"redirect_to": redirect_to_url}
            )
            data, count = (
                self.supabase.from_("user_profile")
                .update({
                    "invitation_token": invitation_token if invitation_token else None,
                    "platform_id": platform_token if platform_token else None
                })
                .eq("user_id", response.user.id)
                .execute()
            )
            return response.user.id
        except Exception as e:
            if str(e) == "A user with this email address has already been registered":
                raise HTTPException(
                    detail=f"An error occurred during inviting user by email {email}: {e}",
                    status_code=status.HTTP_409_CONFLICT,
                )
            else:
                raise HTTPException(
                    detail=f"An error occurred during inviting user by email {email}: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    def delete_user_by_email(self, email: str):
        try:
            data, count = (
                self.supabase.from_("user_profile")
                .select("user_id")
                .eq("user_email", email)
                .execute()
            )
            if not data[1]:
                raise Exception("A user with this email address not exist")
            self.supabase.auth.admin.delete_user(data[1][0]["user_id"])
            return True
        except Exception as e:
            if str(e) == "A user with this email address not exist":
                raise HTTPException(
                    detail=f"An error occurred during deleting user by email {email}: {e}",
                    status_code=status.HTTP_409_CONFLICT,
                )
            else:
                raise HTTPException(
                    detail=f"An error occurred during deleting user by email {email}: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
    def verify_if_user_exist(self, user_email):
        try:
            data, count = (
                self.supabase.from_("user_profile")
                .select("user_id")
                .eq("user_email", user_email)
                .execute()
            )
            if data[1]:
                return True
            return False
        except Exception as e:
            raise HTTPException(
                detail=f"An error occurred during getting user by email{e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    def grant_login_award(self, user_id):
        return self.supabase.rpc("daily_bonus", {"p_user_id":user_id, "p_bonus_amount": EVERY_DAY_CREDIT_INCREMENT}).execute().data

    def get_subscription(self, user_id):
        data, count = (
            self.supabase.from_("user_profile")
            .select("is_premium")
            .eq("user_id", user_id)
            .execute()
        )
        return data[1][0]["is_premium"]

    def set_invitation_token_from_user_profile(self, user_id, invitation_token):
        try:
            data, count = (
                self.supabase.table("user_profile")
                .update({"invitation_token":invitation_token})
                .eq("user_id", user_id)
                .execute()
            )
        except Exception as e:
            raise Exception(
                f"An error occurred during updating invitation token for user {user_id}: {e}"
            )

    def set_platform_id_from_user_profile(self, user_id, platform_id):
        try:
            data, count = (
                self.supabase.table("user_profile")
                .update({"platform_id":platform_id})
                .eq("user_id", user_id)
                .execute()
            )
        except Exception as e:
            raise Exception(
                f"An error occurred during updating platform_id for user {user_id}: {e}"
            )

    def get_invitation_token_from_user_profile(self, user_id):
        try:
            data, count = (
                self.supabase.table("user_profile")
                .select("invitation_token")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["invitation_token"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting invitation token for user {user_id}: {e}"
            )