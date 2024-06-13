import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.users.supabase import UsersSupabase


class User(UsersSupabase):
    def __init__(self, supabase: UsersSupabase):
        self.supabase = supabase

    async def signup(self, email, phone, password):
        return self.supabase.sign_up(email, phone, password)

    async def login(self, email, phone, password):
        auth_response = self.supabase.sign_in_with_password(email, phone, password)
        user_id = auth_response.user.id
        temp_credit = self.supabase.get_temp_credit_by_user_id(user_id)
        perm_credit = self.supabase.get_perm_credit_by_user_id(user_id)
        return auth_response, temp_credit, perm_credit

    async def logout(self):
        return self.supabase.sign_out()

    async def oauth_login(self, provider):
        return self.supabase.sign_in_with_oauth(provider)

    async def get_session(self):
        return self.supabase.get_session()

    async def get_daily_bonus(self, user_id):
        return self.supabase.grant_login_award(user_id)