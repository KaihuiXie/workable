from supabase import Client, ClientOptions, create_client


class SplitChatsTableQuestionSupabase:

    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )

    def client(self):
        return self.supabase

    def get_all_chats(self):
        try:
            response = (
                self.supabase.from_("chats")
                .select("id, question")
                .order("created_at", desc=False)
                .execute()
            )
            return response.data
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats: {e}"
            )

    def get_all_chats_created_after(self, created_timestamp):
        try:
            response = (
                self.supabase.from_("chats")
                .select("id, question")
                .gt("created_at", created_timestamp)
                .order("created_at", desc=False)
                .execute()
            )
            return response.data
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats created after {created_timestamp}: {e}"
            )

    def back_fill_new_columns(self, chat_id, new_question, text_prompt, image_content):
        try:
            response = (
                self.supabase.table("chats")
                .update(
                    {
                        "new_question": new_question,
                        "text_prompt": text_prompt,
                        "image_content": image_content,
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
