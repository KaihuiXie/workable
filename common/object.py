import os
from dotenv import load_dotenv

from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.shared_chats.shared_chats import SharedChat
from src.chats.chats import Chat

# Initalization
load_dotenv()
math_agent = MathAgent(os.getenv("OPENAI_API_KEYS"), os.getenv("WOLFRAM_ALPHA_APP_ID"))
supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
shared_chats = SharedChat(supabase)
chats = Chat(supabase, math_agent=math_agent)
