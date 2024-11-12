from src.users.supabase import UsersSupabase
from src.users.interfaces import (
    LoginResponse,
    UserInfo
)

class User(UsersSupabase):
    def __init__(self, supabase):
        self.supabase: UsersSupabase = supabase

    def login_user(self, email, password):
        response = self.supabase.sign_in_with_password(email, password)
        user_info = UserInfo(
            user_id = response["id"],
            email = response["email"],
            name = response["username"],
            token = response["token"]
        )
        return LoginResponse(user_info = user_info)
    
    def register_user(self, email, password, name):
        response = self.supabase.sign_up_with_email(email, password, name)
        return response
