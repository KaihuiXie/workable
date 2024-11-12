from src.users.supabase import UsersSupabase
from src.users.users import User

url = "https://stuabaechwhrzbjfddyq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN0dWFiYWVjaHdocnpiamZkZHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4NTA2NjcsImV4cCI6MjA0NjQyNjY2N30.yShFh5HH6H-1uKGRSZKJGujlmwPPAw54x-ZTLu1Ssow"

SECRET_KEY = "your_secret_key"

user_services = UsersSupabase(url, key)
users = User(user_services)