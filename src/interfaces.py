from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional, List

# Define the Mode enumeration
class Mode(Enum):
    LEARNER = "learner"
    HELPER = "helper"

    @staticmethod
    def from_string(s):
        if s is None:
            return Mode.HELPER
        try:
            return Mode[s.upper()]
        except KeyError:
            raise ValueError(f"{s} is not a valid Mode")


# Define a Pydantic model for the request data
class QuestionRequest(BaseModel):
    user_id: str
    mode: Mode
    prompt: Optional[str] = None
    image_string: Optional[str] = None


class ChatRequest(BaseModel):
    query: Optional[str] = None
    chat_id: str


class AllChatsRequest(BaseModel):
    user_id: str
