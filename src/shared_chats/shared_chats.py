import json
import logging
from datetime import datetime, timezone

from common.constants import SHARED_CHAT_EXPIRE_TIME, TIME_FORMAT
from src.math_agent.supabase import Supabase
from src.shared_chats.interfaces import CreateSharedChatRequest

# Configure logging
logging.basicConfig(level=logging.INFO)


class SharedChat:
    def __init__(self, supabase: Supabase):
        self.supabase = supabase
        self.expire_time = SHARED_CHAT_EXPIRE_TIME

    def create_shared_chat(self, request: CreateSharedChatRequest):
        chat = self.supabase.get_chat_by_id(request.chat_id)
        shared_chat_id = self.__get_existing_shared_chat_id(
            request.chat_id, chat["updated_at"]
        )
        if shared_chat_id:
            return shared_chat_id
        else:
            return self.supabase.create_shared_chat(
                chat["user_id"],
                request.chat_id,
                chat["updated_at"],
                chat["payload"],
                chat["image_str"],
                chat["question"],
                chat["thumbnail_str"],
                chat["learner_mode"],
                request.is_permanent,
            )

    def get_shared_chat(self, shared_chat_id: str):
        shared_chat = self.supabase.get_shared_chat_by_shared_chat_id(shared_chat_id)
        if self.__is_expired(shared_chat):
            return None
        return shared_chat

    def delete_shared_chat_by_chat_id(self, shared_chat_id: str):
        self.supabase.delete_shared_chat_by_chat_id(shared_chat_id)

    def delete_shared_chat_by_shared_chat_id(self, shared_chat_id: str):
        self.supabase.delete_shared_chat_by_shared_chat_id(shared_chat_id)

    def __get_existing_shared_chat_id(self, chat_id: str, updated_at: str):
        """
        Get existing shared_chat id for given chat_id and updated_at timestamp

        If such a shared_chat exists, update the creat timestamp of this shared_chat
        Return None if no such shared_chat exists
        """
        shared_chat_id = self.supabase.get_shared_chat_by_chat_id_updated_time(
            chat_id, updated_at
        )
        if shared_chat_id:
            self.supabase.update_shared_chat_create_time_to_now(shared_chat_id)
            return shared_chat_id
        else:
            return None

    def __is_expired(self, shared_chat: json):
        created_at = datetime.strptime(shared_chat["created_at"], TIME_FORMAT)
        shared_chat_id = shared_chat["id"]
        is_permanent = shared_chat["is_permanent"]
        if is_permanent or datetime.now(timezone.utc) - created_at < self.expire_time:
            return False
        else:
            self.supabase.delete_shared_chat_by_shared_chat_id(shared_chat_id)
            return True
