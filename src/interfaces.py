from pydantic import BaseModel, field_validator
from typing import Optional, List


# Define a Pydantic model for the request data
class QuestionRequest(BaseModel):
    user_id: str
    prompt: Optional[str] = None
    image_string: Optional[str] = None


class ChatRequest(BaseModel):
    query: Optional[str] = None
    chat_id: str


class AllChatsRequest(BaseModel):
    user_id: str
