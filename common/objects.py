import os

from dotenv import load_dotenv

from src.email.sendgrid import EmailService
from src.stripe.stripe import Stripe
from src.chats.chats import Chat
from src.chats.supabase import ChatsSupabase
from src.credits.credits import Credit
from src.credits.supabase import CreditsSupabase
from src.invitations.invitations import Invitations
from src.invitations.supabase import InvitationsSupabase
from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.shared_chats.shared_chats import SharedChat
from src.shared_chats.supabase import SharedChatsSupabase
from src.url_platforms.supabase import UrlPlatformsSupabase
from src.url_platforms.url_platforms import UrlPlatforms
from src.users.supabase import UsersSupabase
from src.users.users import User
# Initalization
load_dotenv()
supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
math_agent = MathAgent(
    os.getenv("OPENAI_API_KEYS"), os.getenv("WOLFRAM_ALPHA_APP_ID"), supabase
)

shared_chats = SharedChat(SharedChatsSupabase(supabase))
chats = Chat(ChatsSupabase(supabase), math_agent=math_agent)
credits = Credit(CreditsSupabase(supabase))
invitations = Invitations(InvitationsSupabase(supabase))
url_platforms = UrlPlatforms(UrlPlatformsSupabase(supabase))
user_services = UsersSupabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE"))
users = User(user_services)
ems = EmailService(os.getenv("SENDGRID_API"), os.getenv("EMAIL_HEADER"))
payment_service = Stripe(os.getenv("STRIPE_API"), os.getenv("STRIPE_ENDPOINT_KEY"), os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"), ems)