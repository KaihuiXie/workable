from datetime import datetime, timedelta, timezone

import dateutil.parser

from common.constants import INVITATION_BONUS, INVITATION_TOKEN_EXPIRATION
from src.math_agent.supabase import Supabase


def is_invitation_expired(timestamp):
    invitation_expiration = dateutil.parser.parse(timestamp)
    now = datetime.now(timezone.utc)
    # if now is greater than invitation expiration, then it is expired
    return now > invitation_expiration


class InvitationsSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()
        self.table = "invitation"

    def get_invitation_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("invitation")
                .select("id, valid_until")
                .eq("user_id", user_id)
                .execute()
            )

            # case1, if token does not exist, then create a new token
            if len(data[1]) == 0 or not data[1]:
                return self.create_invitation(user_id)

            token = data[1][0]["id"]
            expiration = data[1][0]["valid_until"]

            # case2: if token expired, delete the old one, and then create a new token
            if is_invitation_expired(expiration):
                self.delete_invitation_by_user_id(user_id)
                return self.create_invitation(user_id)

            # case3: return a valid token
            return token
        except Exception as e:
            raise Exception(
                f"An error occurred during getting invitation by user {user_id}: {e}"
            )

    def create_invitation(self, user_id):
        try:
            row_dict = {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S%z"
                ),
                "valid_until": (
                    datetime.now(timezone.utc)
                    + timedelta(days=INVITATION_TOKEN_EXPIRATION)
                ).strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            data, count = self.supabase.table("invitation").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during creating invitation for user {user_id}: {e}"
            )

    def is_eligible_for_reward(self, token, user_id):
        try:
            data, count = (
                self.supabase.table("user_profile")
                .select("is_rewarded", "created_at", "user_email")
                .eq("user_id", user_id)
                .execute()
            )
            is_rewarded, created_at, user_email = (
                data[1][0]["is_rewarded"],
                data[1][0]["created_at"],
                data[1][0]["user_email"],
            )
            data, count = (
                self.supabase.table("invitation")
                .select("created_at")
                .eq("id", token)
                .execute()
            )
            token_date = data[1][0]["created_at"]
            if is_rewarded:
                return False, user_email
            if token_date > created_at:
                return False, user_email
            self.supabase.table("user_profile").update({"is_rewarded": True}).eq(
                "user_id", user_id
            ).execute()
            return True, user_email
        except Exception as e:
            raise Exception(
                f"An error occurred during getting information from user_id {user_id}: {e}"
            )

    def get_referee_list(self, user_id):
        try:
            response = (
                self.supabase.table("referee_list")
                .select("*")
                .eq("referrer_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting invitation for user {user_id}: {e}"
            )

    def update_referee_list(self, user_id, guest_email):
        try:
            row_dict = {
                "referrer_id": user_id,
                "guest_email": guest_email,
                "join_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
                "bonus": INVITATION_BONUS,
            }
            data, count = self.supabase.table("referee_list").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during updateing referee list for user {user_id} and guest {guest_email}: {e}"
            )

    def delete_invitation_by_user_id(self, user_id):
        try:
            response = (
                self.supabase.table("invitation")
                .delete()
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting invitation for user {user_id}: {e}"
            )

    def get_referrer_id_by_invitation_token(self, token):
        if token == "":
            return False, ""
        try:
            data, count = (
                self.supabase.from_("invitation")
                .select("user_id, valid_until")
                .eq("id", token)
                .execute()
            )

            user_id = data[1][0]["user_id"]
            expiration = data[1][0]["valid_until"]

            if is_invitation_expired(expiration):
                return False, user_id
            return True, user_id
        except Exception as e:
            return False, ""

    def update_notification(self, user_id, email):
        try:
            response = (
                self.supabase.table("referee_list")
                .update({"isNotify": True})
                .eq("referrer_id", user_id)
                .eq("guest_email", email)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating notification for user {user_id} and guest email {email}: {e}"
            )

    def get_bonus(self, user_id):
        prev_perm_credit = self.get_perm_credit_by_user_id(user_id)
        self.update_perm_credit_by_user_id(user_id, prev_perm_credit + INVITATION_BONUS)

    def get_perm_credit_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("perm_credit")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["perm_credit"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting perm credit by user {user_id}: {e}"
            )

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
