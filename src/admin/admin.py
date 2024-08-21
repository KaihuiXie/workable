from fastapi import HTTPException, status
from supabase import Client, ClientOptions, create_client


class AdminSupabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )
        
    def client(self):
        return self.supabase
    
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