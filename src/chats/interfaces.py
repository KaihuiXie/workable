from enum import Enum
from typing import Optional

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ValidationError, model_validator


class ChatOwnershipError(Exception):
    """Custom exception for chat ownership errors."""

    def __init__(self, message):
        super().__init__(message)


# Define the Mode enumeration
class Mode(str, Enum):
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


class Language(str, Enum):
    ENGLISH = "EN"
    SPANISH = "ES"
    FRENCH = "FR"
    GERMAN = "DE"
    CHINESE = "ZH"
    JAPANESE = "JA"
    RUSSIAN = "RU"

    @staticmethod
    def from_string(s):
        if s is None:
            return Language.ENGLISH
        try:
            return Language[s.upper()]
        except KeyError:
            raise ValueError(f"{s} is not a valid Language")


class ChatColumn(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PAYLOAD = "payload"
    IMAGE_STR = "image_str"
    LEARNER_MODE = "learner_mode"
    USER_ID = "user_id"
    THUMBNAIL_STR = "thumbnail_str"
    QUESTION = "question"
    TEXT_PROMPT = "text_prompt"
    IMAGE_CONTENT = "image_content"
    WOLFRAM_QUERY = "wolfram_query"
    WOLFRAM_ANSWER = "wolfram_answer"
    WOLFRAM_IMAGE = "wolfram_image"


class UploadQuestionRequest(BaseModel):
    chat_id: str
    mode: Mode
    prompt: Optional[str] = None
    image_file: Optional[UploadFile] = None

    @model_validator(mode="before")
    def check_image_str_and_prompt(cls, values):
        image_file, prompt = values.get("image_file"), values.get("prompt")
        if not image_file and not prompt:
            raise ValueError("If image_file is empty, then prompt must exist.")
        return values

    @staticmethod
    # Dependency to parse QuestionRequest model from form data
    async def parse_question_request(
        chat_id: str = Form(...),
        mode: Mode = Form(...),
        prompt: Optional[str] = Form(None),
        image_file: Optional[UploadFile] = File(None),
    ) -> "UploadQuestionRequest":

        # Construct the QuestionRequest object
        return UploadQuestionRequest(
            chat_id=chat_id, mode=mode, prompt=prompt, image_file=image_file
        )
        # except ValidationError as e:
        #     # Handle validation errors, e.g., by raising an HTTP exception
        #     raise HTTPException(status_code=400, detail="Invalid request data")


class ChatRequest(BaseModel):
    query: Optional[str] = None
    chat_id: str
    language: Optional[Language] = None


class NewChatRequest(BaseModel):
    user_id: str
