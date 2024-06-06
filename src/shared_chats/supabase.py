from datetime import datetime, timezone

from common.constants import TIME_FORMAT
from src.supabase.supabase import Supabase


class SharedChatsSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()
        self.table = "shared_chats"

    def create_shared_chat(
        self,
        user_id,
        chat_id,
        updated_at,
        payload,
        image_str,
        question,
        thumbnail_str,
        learner_mode,
        is_permanent=False,
    ):
        try:
            row_dict = {
                "user_id": user_id,
                "chat_id": chat_id,
                "updated_at": updated_at,
                "payload": payload,
                "image_str": image_str,
                "question": question,
                "thumbnail_str": thumbnail_str,
                "leaner_mode": learner_mode,
                "is_permanent": is_permanent,
            }
            data, count = self.supabase.table("shared_chats").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(f"An error occurred during creating a shared chat: {e}")

    def delete_shared_chat_by_shared_chat_id(self, shared_chat_id):
        try:
            response = (
                self.supabase.table("shared_chats")
                .delete()
                .eq("id", shared_chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting shared chat {shared_chat_id}: {e}"
            )

    def delete_shared_chat_by_chat_id(self, chat_id):
        """Delete all shared_chat(s) linked to the chat specified by chat_id."""
        try:
            response = (
                self.supabase.table("shared_chats")
                .delete()
                .eq("chat_id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting shared chats {chat_id}: {e}"
            )

    def get_shared_chat_by_shared_chat_id(self, shared_chat_id):
        try:
            data, count = (
                self.supabase.from_("shared_chats")
                .select("*")
                .eq("id", shared_chat_id)
                .execute()
            )
            return data[1][0]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting shared chat by shared_chat_id {shared_chat_id}: {e}"
            )

    def get_shared_chats_by_chat_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("shared_chats")
                .select("*")
                .eq("chat_id", chat_id)
                .execute()
            )
            return data[1]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting shared chat by chat_id {chat_id}: {e}"
            )

    def update_shared_chat_create_time_to_now(self, shared_chat_id):
        try:
            response = (
                self.supabase.table("shared_chats")
                .update(
                    {"created_at": datetime.now(timezone.utc).strftime(TIME_FORMAT)}
                )
                .eq("id", shared_chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating create time for shared chat {shared_chat_id}: {e}"
            )

    def update_shared_chat_create_time(self, shared_chat_id, updated_at):
        try:
            response = (
                self.supabase.table("shared_chats")
                .update({"created_at": updated_at})
                .eq("id", shared_chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating create time for shared chat {shared_chat_id}: {e}"
            )

    def get_shared_chat_by_chat_id_updated_time(self, chat_id, updated_at):
        try:
            data, count = (
                self.supabase.from_("shared_chats")
                .select("id")
                .eq("chat_id", chat_id)
                .eq("updated_at", updated_at)
                .execute()
            )
            if len(data[1]) == 0:
                return None
            else:
                return data[1][0]["id"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting shared chat by chat_id {chat_id} and updated_at {updated_at}: {e}"
            )
