from supabase import Client, ClientOptions, create_client


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
                "image_str": "",
                "thumbnail_str": "",
                "user_id": user_id,
                "question": "",
                "payload": "",
                "learner_mode": False,
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
