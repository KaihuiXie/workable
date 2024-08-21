import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.users.supabase import UsersSupabase


class User(UsersSupabase):
    def __init__(self, supabase):
        self.supabase: UsersSupabase = supabase

    def signup(self, email, phone, password):
        return self.supabase.sign_up(email, phone, password)

    def login(self, email, password):
        auth_response = self.supabase.sign_in_with_password(email, password)
        return auth_response.session.access_token

    def logout(self, jwt):
        self.supabase.sign_out(jwt)

    def oauth_login(self, provider, token):
        return self.supabase.sign_in_with_oauth(provider, token)

    def exchange_code(self, auth_code):
        return self.supabase.exchange_code_for_session(auth_code)
    
    def get_session(self):
        return self.supabase.get_session()

    def get_daily_bonus(self, user_id):
        return self.supabase.grant_login_award(user_id)
