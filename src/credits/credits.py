import logging

from src.credits.interfaces import DecrementCreditRequest, UpdateCreditRequest
from src.credits.supabase import CreditsSupabase

# Configure logging
logging.basicConfig(level=logging.INFO)


class Credit:
    def __init__(self, supabase: CreditsSupabase):
        self.supabase = supabase

    def create_credit(self, user_id: str):
        return self.supabase.create_credit(user_id)

    def get_credit(self, user_id: str):
        temp_credit = self.supabase.get_temp_credit_by_user_id(user_id)
        perm_credit = self.supabase.get_perm_credit_by_user_id(user_id)
        return temp_credit, perm_credit

    def get_temp_credit(self, user_id: str):
        return self.supabase.get_temp_credit_by_user_id(user_id)

    def get_perm_credit(self, user_id: str):
        return self.supabase.get_perm_credit_by_user_id(user_id)

    def update_temp_credit(self, request: UpdateCreditRequest):
        return self.supabase.update_temp_credit_by_user_id(
            request.user_id, request.credit
        )

    def update_perm_credit(self, request: UpdateCreditRequest):
        return self.supabase.update_perm_credit_by_user_id(
            request.user_id, request.credit
        )

    def decrement_credit(self, user_id):
        return self.supabase.decrement_credit(user_id)
