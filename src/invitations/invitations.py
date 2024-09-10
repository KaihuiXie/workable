import logging

from src.invitations.supabase import InvitationsSupabase
from src.invitations.interfaces import RefereeEntity
# Configure logging
logging.basicConfig(level=logging.INFO)


class Invitations(InvitationsSupabase):
    def __init__(self, supabase):
        self.supabase: InvitationsSupabase = supabase

    def get_referrer(self, invitation_token: str):
        return self.supabase.get_referrer_id_by_invitation_token(invitation_token)

    def get_invitation_by_user_id(self, user_id: str):
        return self.supabase.get_invitation_by_user_id(user_id)

    def get_invitation_by_token(self, invitation_token: str, user_id: str):
        original_invitation_token = self.supabase.get_invitation_token_from_user_profile(user_id)
        if invitation_token and invitation_token!=original_invitation_token: #Already claim the bonus
            return False
        if not invitation_token: #no invitation token found if it is oauth or sign up
            invitation_token = original_invitation_token 
        if not invitation_token: #no invitation at all
            return False
        is_invited, referrer_id = self.supabase.get_referrer_id_by_invitation_token(
            invitation_token
        )
        if referrer_id == user_id:
            return False
        is_eligible = False
        if is_invited:
            is_eligible, user_email = self.supabase.is_eligible_for_reward(
                invitation_token, user_id
            )
            if is_eligible:
                self.supabase.update_referee_list(referrer_id, user_email)
                self.supabase.get_bonus(user_id)
                self.supabase.get_bonus(referrer_id)
        return is_eligible

    def get_referee_list(self, user_id: str):
        return self.supabase.get_referee_list(user_id)
         

    def get_notification_list(self, user_id: str):
        referee_list = self.get_referee_list(user_id)
        response_list = []
        for referee in referee_list.data:
            if not referee["isNotify"]:
                response_list.append(referee["guest_email"])
        return response_list

    def update_notification(self, user_id: str, guest_email: list):
        for email in guest_email:
            self.supabase.update_notification(user_id, email)
        return True
