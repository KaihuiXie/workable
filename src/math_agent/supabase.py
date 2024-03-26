from supabase import create_client, Client
import uuid
from datetime import datetime, timezone
import json


class Supabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)

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
