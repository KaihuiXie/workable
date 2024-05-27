from datetime import datetime, timezone

import dateutil.parser

from common.constants import (
    COST_PER_QUESTION,
    DEFAULT_CREDIT,
    EVERY_DAY_CREDIT_INCREMENT,
    INVITATION_BONUS,
)
from src.math_agent.supabase import Supabase


def is_same_day(date: datetime):
    return date.date() == datetime.utcnow().date()


class CreditsSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()
        self.table = "credits"

    # for everyday login & refresh every Sunday
    def update_temp_credit_by_user_id(self, user_id, amount):
        try:
            if amount < 0:
                raise ValueError(f"User {user_id}: credit can't be negative.")
            response = (
                self.supabase.table("credits")
                .update({"temp_credit": amount})
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating temp credit for user {user_id}: {e}"
            )

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

    # 1. Check if user is eligible for login award
    # 1.1 get last_award_time
    # 1.2 compare with today
    # 2. if 1 is yes
    # 2.1 get_prev_temp_credit
    # 2.2 update_temp_credit
    # 2.3 update last_award_time
    def grant_login_award(self, user_id):
        last_award_time = self.get_last_award_time_by_user_id(user_id)
        is_eligible = not is_same_day(dateutil.parser.parse(last_award_time))
        if not is_eligible:
            return
        prev_temp_credit = self.get_temp_credit_by_user_id(user_id)
        self.update_temp_credit_by_user_id(
            user_id, prev_temp_credit + EVERY_DAY_CREDIT_INCREMENT
        )
        self.update_last_award_time_by_user_id(user_id)

    def get_bonus(self, user_id):
        prev_perm_credit = self.get_perm_credit_by_user_id(user_id)
        self.update_perm_credit_by_user_id(user_id, prev_perm_credit + INVITATION_BONUS)

    def update_last_award_time_by_user_id(self, user_id):
        try:
            response = (
                self.supabase.table("credits")
                .update(
                    {
                        "last_award_time": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%S%z"
                        )
                    }
                )
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating perm credit for user {user_id}: {e}"
            )

    def get_last_award_time_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("last_award_time")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["last_award_time"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting last login by user email {user_id}: {e}"
            )
