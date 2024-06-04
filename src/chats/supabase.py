from src.math_agent.supabase import Supabase
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

    def get_chat_payload_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_(self.table)
                .select("payload")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["payload"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat payload by chat_id {chat_id}: {e}"
            )

    def get_chat_image_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_(self.table)
                .select("image_str")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["image_str"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting question image by chat_id {chat_id}: {e}"
            )

    def get_chat_question_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_(self.table)
                .select("question")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["question"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat question by chat_id {chat_id}: {e}"
            )

    def fulfill_empty_chat(
        self, chat_id, image_str, thumbnail_str, question, is_learner_mode
    ):
        try:
            payload = self.question_to_payload(question)
            response = (
                self.supabase.table("chats")
                .update(
                    {
                        "image_str": image_str,
                        "thumbnail_str": thumbnail_str,
                        "payload": payload,
                        "question": question,
                        "learner_mode": is_learner_mode,
                    }
                )
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during fulfill fields for chat {chat_id}: {e}"
            )

    def get_all_chats(self, user_id):
        try:
            response = (
                self.supabase.from_("chats")
                .select(
                    "id, thumbnail_str, question, learner_mode, created_at",
                    count="exact",
                )
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            self.grant_login_award(user_id)
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats for user {user_id}: {e}"
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
