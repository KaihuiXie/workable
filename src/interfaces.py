from enum import Enum
from pydantic import BaseModel, model_validator
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
class SignUpRequest(BaseModel):
    email: str
    password: str
    redirect_to: Optional[str] = None


class SignInRequest(BaseModel):
    email: str
    password: str
    redirect_to: str


class QuestionRequest(BaseModel):
    user_id: str
    mode: Mode
    prompt: Optional[str] = None
    image_string: Optional[str] = None

    @model_validator(mode="before")
    def check_image_str_and_prompt(cls, values):
        image_string, prompt = values.get("image_string"), values.get("prompt")
        if not image_string and not prompt:
            raise ValueError("If image_string is empty, then prompt must exist.")
        return values


class ChatRequest(BaseModel):
    query: Optional[str] = None
    chat_id: str


class AllChatsRequest(BaseModel):
    user_id: str
