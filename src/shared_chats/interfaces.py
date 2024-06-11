from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from src.chats.interfaces import ChatColumn


class NewSharedChatRequest(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat to be shared")
    is_permanent: Optional[bool] = Field(
        True, description="Whether this shared chat is permanent"
    )


class NewSharedChatResponse(BaseModel):
    shared_chat_id: str = Field(..., description="The ID of the shared chat")


class GetSharedChatResponse(BaseModel):
    payload: Optional[Dict[str, Any]] = Field(None, description="Chat history")
    question: Optional[str] = Field(None, description="Chat question")
    image_str: Optional[str] = Field(None, description="Image string in base64 format")
    text_prompt: Optional[str] = Field(None, description="Chat text prompt")
    image_content: Optional[str] = Field(None, description="Chat image content")

    def __init__(self, chat, /, **data: Any):
        super().__init__(**data)
        self.payload = chat[ChatColumn.PAYLOAD]
        self.question = chat[ChatColumn.QUESTION]
        self.image_str = chat[ChatColumn.IMAGE_STR]
        self.text_prompt = chat[ChatColumn.TEXT_PROMPT]
        self.image_content = chat[ChatColumn.IMAGE_CONTENT]


class DeleteSharedChatResponse(BaseModel):
    shared_chat_id: list[str] = Field(
        ..., description="A list of the IDs of the deleted shared chat"
    )
