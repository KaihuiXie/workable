import os

from src.users.supabase import UsersSupabase
from src.users.users import User

url = "https://stuabaechwhrzbjfddyq.supabase.co"
key = ""
user_services = UsersSupabase(url, key)
users = User(user_services)