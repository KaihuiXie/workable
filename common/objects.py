import os

from dotenv import load_dotenv

from src.chats.chats import Chat
from src.credits.credits import Credit
from src.invitations.invitations import Invitations
from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.shared_chats.shared_chats import SharedChat
from src.users.users import User

# Initalization
load_dotenv()
math_agent = MathAgent(os.getenv("OPENAI_API_KEYS"), os.getenv("WOLFRAM_ALPHA_APP_ID"))
supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
shared_chats = SharedChat(supabase)
chats = Chat(supabase, math_agent=math_agent)
credits = Credit(supabase)
invitations = Invitations(supabase)
users = User(supabase)
