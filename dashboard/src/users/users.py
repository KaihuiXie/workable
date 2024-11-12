from src.users.supabase import UsersSupabase

class User(UsersSupabase):
    def __init__(self, supabase):
        self.supabase: UsersSupabase = supabase

    def login_user(self, email):
        response = self.supabase.sign_in_with_password(email)
        return response
    
    def register_user(self, email, password, name):
        response = self.supabase.sign_up_with_email(email, password, name)
        return response
