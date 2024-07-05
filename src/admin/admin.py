from supabase import Client, ClientOptions, create_client


class AdminSupabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )

    def invite_user_by_email(self, email: str, redirect_to_url: str):
        try:
            response = self.supabase.auth.admin.invite_user_by_email(
                email, options={"redirect_to": redirect_to_url}
            )
            return response.user.id
        except Exception as e:
            raise Exception(
                f"An error occurred during inviting user by email {email}: {e}"
            )
