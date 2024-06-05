from datetime import datetime, timezone

import dateutil.parser
from supabase import Client, ClientOptions, create_client

from common.constants import EVERY_DAY_CREDIT_INCREMENT


def is_same_day(date: datetime):
    return date.date() == datetime.utcnow().date()


class Supabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )

    def client(self):
        return self.supabase

    ### Shared function
    def get_chat_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats").select("*").eq("id", chat_id).execute()
            )
            return data[1][0]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat question by chat_id {chat_id}: {e}"
            )

    ### Shared function
    def create_empty_chat(self, user_id):
        try:
            row_dict = {
                "user_id": user_id,
            }
            data, count = self.supabase.table("chats").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(f"An error occurred during creating an empty chat: {e}")

    ### Shared function
    def get_chats_by_ids(self, chat_ids):
        try:
            response = (
                self.supabase.from_("chats")
                .select("id, thumbnail_str, question, learner_mode", count="exact")
                .in_("id", chat_ids)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting chats for chat_ids {chat_ids}: {e}"
            )

    ### Shared function
    def update_thumbnail(self, chat_id, thumbnail_str):
        try:
            response = (
                self.supabase.table("chats")
                .update({"thumbnail_str": thumbnail_str})
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating thumbnail_str for chat {chat_id}: {e}"
            )

    ### Shared function
    def delete_chat_by_id(self, chat_id):
        try:
            response = self.supabase.table("chats").delete().eq("id", chat_id).execute()
            return response
        except Exception as e:
            raise Exception(f"An error occurred during deleting chat {chat_id}: {e}")

    ### Shared function
    def get_temp_credit_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("temp_credit")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["temp_credit"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting temp credit by user {user_id}: {e}"
            )

    ### Shared function
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

    def update_columns_by_primary_id(
        self, table: str, primary_id: str, columns: dict[str, str]
    ):
        try:
            response = (
                self.supabase.table(table)
                .update(columns)
                .eq("id", primary_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating {list(columns.keys())} for {table} {primary_id}: {e}"
            )
