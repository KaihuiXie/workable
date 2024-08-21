from src.math_agent.supabase import Supabase


class UsersSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()

    def auth(self):
        return self.auth

    def sign_up(self, email: str, phone: str, password: str):
        try:
            res = self.supabase.auth.sign_up(
                {"email": email, "phone": phone, "password": password}
            )
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

    def exchange_code_for_session(self, auth_code: str):
        try:
            res = self.supabase.auth.exchange_code_for_session(
                {
                    "auth_code": auth_code,
                    "code_verifier":" "
                }
            )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing in user with oauth provider: {e}"
            )

    def sign_out(self, jwt):
        try:
            self.supabase.auth.admin.sign_out(jwt)
        except Exception as e:
            raise Exception(f"An error occurred during signing out: {e}")

    def get_session(self):
        try:
            session = self.supabase.auth.get_session()
            return session
        except Exception as e:
            raise Exception(f"An error occurred during getting session: {e}")
