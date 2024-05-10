import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


class User:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

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
