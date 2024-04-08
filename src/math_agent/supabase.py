from supabase import create_client, Client, ClientOptions
import uuid
from datetime import datetime, timezone
import json


def is_same_day(date: datetime):
    return date.date() == datetime.today().date()


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
            last_login = self.get_last_login_by_user_email(email)
            if not is_same_day(last_login):
                self.update_temp_credit_by_email(email, 20)
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

    def get_chat_by_id(self, chat_id):
        try:
            response = (
                self.supabase.from_("chats").select("*").eq("id", chat_id).execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during getting a chat by chat_id {chat_id}: {e}"
            )

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
                .select("id, question", count="exact")
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats for user {user_id}: {e}"
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

    @staticmethod
    def question_to_payload(question):
        message = [{"role": "assistant", "content": question}]
        payload = {"messages": message}
        return payload

    # for everyday login & refresh every Sunday
    def update_temp_credit_by_email(self, user_email, amount):
        try:
            response = (
                self.supabase.table("users")
                .update({"temp_credit": amount})
                .eq("email", user_email)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating temp credit for user {user_email}: {e}"
            )

    # for invitations and purchases
    def update_perm_credit_by_email(self, user_email, amount):
        try:
            response = (
                self.supabase.table("users")
                .update({"perm_credit": amount})
                .eq("email", user_email)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating perm credit for user {user_email}: {e}"
            )

    def get_temp_credit_by_email(self, user_email):
        try:
            data, count = (
                self.supabase.from_("users")
                .select("temp_credit")
                .eq("email", user_email)
                .execute()
            )
            return data[1][0]["temp_credit"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting temp credit by user {user_email}: {e}"
            )

    def get_perm_credit_by_email(self, user_email):
        try:
            data, count = (
                self.supabase.from_("users")
                .select("perm_credit")
                .eq("email", user_email)
                .execute()
            )
            return data[1][0]["perm_credit"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting perm credit by user {user_email}: {e}"
            )

    def get_credit_by_email(self, user_email):
        try:
            return self.get_temp_credit_by_email(user_email) + self.get_perm_credit_by_email(user_email)
        except Exception as e:
            raise Exception(
                f"An error occurred during getting credit by user {user_email}: {e}"
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

    def get_last_login_by_user_email(self, user_email):
        try:
            data, count = (
                self.supabase.auth.from_("users")
                .select("last_sign_in_at")
                .eq("email", user_email)
                .execute()
            )
            return data[1][0]["last_sign_in_at"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting last login by user email {user_email}: {e}"
            )

    def decrement_credit(self, user_id):
        try:
            user_email = self.get_user_email_by_id(user_id)
            temp_credit = self.get_temp_credit_by_email(user_email)
            perm_credit = self.get_perm_credit_by_email(user_email)
            if temp_credit > 0:
                self.update_temp_credit_by_email(user_email, temp_credit - 1)
            elif perm_credit > 0:
                self.update_perm_credit_by_email(user_email, perm_credit - 1)
            else:
                raise ValueError(f"User {user_id}: {user_id} doesn't have enough credit.")
        except Exception as e:
            raise Exception(
                f"An error occurred during decrement credit from user {user_id}: {e}"
            )

    def get_user_email_by_id(self, user_id):
        try:
            data, count = (
                self.supabase.auth.from_("users")
                .select("user_email")
                .eq("id", user_id)
                .execute()
            )
            return data[1][0]["user_email"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting last login by user id {user_id}: {e}"
            )
