from supabase import create_client, Client, ClientOptions
import uuid
from datetime import datetime, timezone
import json
import datetime as dt

from src.math_agent.constant import (
    EVERY_DAY_CREDIT_INCREMENT,
    COST_PER_QUESTION,
    DEFAULT_CREDIT,
    INVITATION_TOKEN_EXPIRATION,
)


def is_same_day(date: datetime):
    return date.date() == datetime.today().date()


def is_invitation_expired(timestamp):
    invitation_expiration = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    now = datetime.now(timezone.utc)
    # if now is greater than invitation expiration, then it is expired
    return now > invitation_expiration


class Supabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )

    def client(self):
        return self.supabase

    def auth(self):
        return self.auth

    def sign_up(self, email: str, password: str):
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password})

            # create a credit record for the account
            self.create_credit(res.user.user_id)

            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing up user with email {email}: {e}"
            )

    def sign_in_with_password(self, email: str, password: str):
        try:
            res = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            # if it is the first login of the day, increment the credit
            user_id = res.user.user_id
            last_login = res.user.last_sign_in_at
            if not is_same_day(last_login):
                prev_credit = self.get_credit_by_user_id(user_id)
                self.update_temp_credit_by_user_id(
                    user_id, prev_credit + EVERY_DAY_CREDIT_INCREMENT
                )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing in user with email {email}: {e}"
            )

    def sign_out(self):
        try:
            res = self.supabase.auth.sign_out()
            return res
        except Exception as e:
            raise Exception(f"An error occurred during signing out: {e}")

    def get_user(self):
        try:
            user = self.supabase.auth.get_user()
            return user
        except Exception as e:
            raise Exception(f"An error occurred during getting user: {e}")

    def get_chat_payload_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("payload")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["payload"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat payload by chat_id {chat_id}: {e}"
            )

    def get_chat_question_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("question")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["question"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat question by chat_id {chat_id}: {e}"
            )

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

    def create_chat(self, image_str, user_id, question, is_learner_mode):
        try:
            payload = self.question_to_payload(question)
            row_dict = {
                "image_str": image_str,
                "user_id": user_id,
                "question": question,
                "payload": payload,
                "learner_mode": is_learner_mode,
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
            raise Exception(f"An error occurred during creating a chat: {e}")

    def get_all_chats(self, user_id):
        try:
            response = (
                self.supabase.from_("chats")
                .select("id, question, learner_mode", count="exact")
                .eq("user_id", user_id)
                .execute()
            )
            self.grant_login_award(user_id)
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats for user {user_id}: {e}"
            )

    def get_chats_by_ids(self, chat_ids):
        try:
            response = (
                self.supabase.from_("chats")
                .select("id, question, learner_mode", count="exact")
                .in_("id", chat_ids)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting chats for chat_ids {chat_ids}: {e}"
            )

    def update_payload(self, chat_id, payload):
        try:
            response = (
                self.supabase.table("chats")
                .update({"payload": payload})
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during upserting payload for chat {chat_id}: {e}"
            )

    def delete_chat_by_id(self, chat_id):
        try:
            response = self.supabase.table("chats").delete().eq("id", chat_id).execute()
            return response
        except Exception as e:
            raise Exception(f"An error occurred during deleting chat {chat_id}: {e}")

    @staticmethod
    def question_to_payload(question):
        message = [{"role": "assistant", "content": question}]
        payload = {"messages": message}
        return payload

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

    def get_credit_by_user_id(self, user_id):
        try:
            return self.get_temp_credit_by_user_id(
                user_id
            ) + self.get_perm_credit_by_user_id(user_id)
        except Exception as e:
            raise Exception(
                f"An error occurred during getting credit by user {user_id}: {e}"
            )

    def get_user_id_by_chat_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("user_id")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["user_id"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting user_id by chat {chat_id}: {e}"
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
        is_eligible = not is_same_day(
            datetime.strptime(last_award_time, "%Y-%m-%dT%H:%M:%S%z")
        )
        if not is_eligible:
            return
        prev_temp_credit = self.get_temp_credit_by_user_id(user_id)
        self.update_temp_credit_by_user_id(
            user_id, prev_temp_credit + EVERY_DAY_CREDIT_INCREMENT
        )
        self.update_last_award_time_by_user_id(user_id)

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

    def get_invitation_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("invitation")
                .select("id, valid_until")
                .eq("user_id", user_id)
                .execute()
            )

            token = data[1][0]["id"]
            expiration = data[1][0]["valid_until"]

            # case1, if token does not exist, then create a new token
            if token == "":
                return self.create_invitation(user_id)

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
                        + dt.timedelta(days=INVITATION_TOKEN_EXPIRATION)
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
            raise Exception(f"An error occurred during creating invitation for user {user_id}: {e}")

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
            return ""
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
                return ""
            return user_id
        except Exception as e:
            return ""
