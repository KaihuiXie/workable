from datetime import datetime, timezone

from common.constants import (
    COST_PER_QUESTION,
    DEFAULT_CREDIT,
    EVERY_DAY_CREDIT_INCREMENT,
    INVITATION_BONUS,
)
from src.math_agent.supabase import Supabase


class CreditsSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()
        self.table = "credits"

    # for invitations and purchases
    def update_perm_credit_by_user_id(self, user_id, amount):
        try:
            if amount < 0:
                raise ValueError(f"User {user_id}: credit can't be negative.")
            response = (
                self.supabase.table("credits")
                .update({"perm_credit": amount})
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating perm credit for user {user_id}: {e}"
            )

    def get_credit_by_user_id(self, user_id):
        try:
            return self.get_temp_credit_by_user_id(
                user_id
            ) + self.get_perm_credit_by_user_id(user_id)
        except Exception as e:
            raise Exception(
                f"An error occurred during getting credit by user {user_id}: {e}"
            )

    def decrement_credit(self, user_id):
        try:
            temp_credit = self.get_temp_credit_by_user_id(user_id)
            perm_credit = self.get_perm_credit_by_user_id(user_id)
            if temp_credit >= COST_PER_QUESTION:
                self.update_temp_credit_by_user_id(
                    user_id, temp_credit - COST_PER_QUESTION
                )
            elif perm_credit >= COST_PER_QUESTION:
                self.update_perm_credit_by_user_id(
                    user_id, perm_credit - COST_PER_QUESTION
                )
            else:
                raise ValueError(
                    f"User {user_id}: {user_id} doesn't have enough credits."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during decrement credit from user {user_id}: {e}"
            )

    def create_credit(self, user_id):
        try:
            row_dict = {
                "user_id": user_id,
                "temp_credit": DEFAULT_CREDIT,
                "perm_credit": DEFAULT_CREDIT,
                "last_award_time": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S%z"
                ),
            }
            data, count = self.supabase.table("credits").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(f"An error occurred during creating a user credit: {e}")

    def delete_credit(self, user_id):
        try:
            response = (
                self.supabase.table("credits").delete().eq("user_id", user_id).execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting credits for user {user_id}: {e}"
            )

    def get_last_sign_in_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("last_sign_in_at")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["last_sign_in_at"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting last login by user email {user_id}: {e}"
            )

    def get_bonus(self, user_id):
        prev_perm_credit = self.get_perm_credit_by_user_id(user_id)
        self.update_perm_credit_by_user_id(user_id, prev_perm_credit + INVITATION_BONUS)
