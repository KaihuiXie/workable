from src.supabase.interfaces import ChatColumn
from src.supabase.supabase import Supabase
from src.utils import generate_thumbnail_string_from_image_string


class ChatsSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()
        self.table = "chats"

    def user_has_access(self, chat_id, user_id) -> bool:
        try:
            data, count = (
                self.supabase.from_(self.table)
                .select("id")
                .eq("id", chat_id)
                .eq("user_id", user_id)
                .execute()
            )
            return len(data[1]) > 0
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat by chat_id {chat_id} and user_id {user_id}: {e}"
            )

    def get_chat_columns_by_id(self, chat_id: str, columns: list[ChatColumn]):
        try:
            columns = ", ".join(columns)
            data, count = (
                self.supabase.from_(self.table)
                .select(columns, count="exact")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting {columns} by chat_id {chat_id}: {e}"
            )

    def get_chat_column_by_id(self, chat_id: str, column: ChatColumn):
        try:
            data, count = (
                self.supabase.from_(self.table)
                .select(column)
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0][column]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting {column} by chat_id {chat_id}: {e}"
            )

    def get_all_chats_columns_by_user_id(self, user_id: str, columns: list[ChatColumn]):
        try:
            columns = ", ".join(columns)
            response = (
                self.supabase.from_("chats")
                .select(columns, count="exact")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            # TODO: move grant award logic out
            self.grant_login_award(user_id)
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats for user {user_id}: {e}"
            )

    def update_chat_columns_by_id(self, chat_id: str, columns: dict[ChatColumn:str]):
        try:
            response = (
                self.supabase.table(self.table)
                .update(columns)
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating {list(columns.keys())} for chat {chat_id}: {e}"
            )

    def backfill_thumbnail_str(self, chat_ids):
        for chat_id in chat_ids:
            try:
                data, count = (
                    self.supabase.from_("chats")
                    .select("thumbnail_str, image_str", count="exact")
                    .eq("id", chat_id)
                    .execute()
                )

                if not data[1][0]["thumbnail_str"] and data[1][0]["image_str"]:
                    print("Backfill thumbnail_str")
                    thumbnail_str = generate_thumbnail_string_from_image_string(
                        data[1][0]["image_str"]
                    )
                    self.update_thumbnail(chat_id, thumbnail_str)
            except Exception as e:
                raise Exception(
                    f"An error occurred during backfilling thumbnail for chat {chat_id}: {e}"
                )

    @staticmethod
    def question_to_payload(question):
        message = [{"role": "assistant", "content": question}]
        payload = {"messages": message}
        return payload

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
                f"An error occurred during updating payload for chat {chat_id}: {e}"
            )

    def update_question(self, chat_id, question):
        try:
            response = (
                self.supabase.table("chats")
                .update({"question": question})
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating question for chat {chat_id}: {e}"
            )
