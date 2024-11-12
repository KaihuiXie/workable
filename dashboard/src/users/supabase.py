from supabase import Client, create_client

class UsersSupabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)
    
    def sign_in_with_password(self, email, password):
        response = (
            self.supabase
                .table("users")
                .select("*")
                .match({"email": email, "password": password})
                .execute()
        )
        if response.data:
            return response.data[0]
        else:
            print("No matching record found in database.")
            return None
        
    def sign_up_with_email(self, email, password, name):
        if self.has_user(email):
            return None
        
        response = (
            self.supabase
            .table("users")
            .insert({"email": email, "password": password, "username": name})
            .execute()
        )
        if response:
            return response
        else:
            print("Error occurred during insertion.")
            return None  # Handle as needed


    def has_user(self, email):
        existing_user_response = (
            self.supabase.table("users")
            .select("*")
            .eq("email", email)
            .execute()
        )
        if existing_user_response.data:
            print("User already exists.")
            return True 