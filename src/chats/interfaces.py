import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, ValidationError, model_validator


class ChatOwnershipError(Exception):
    """Custom exception for chat ownership errors."""

    def __init__(self, message):
        super().__init__(message)


class AuthorizationError(Exception):
    """Custom exception for authorization errors. usually happens when frontend doesn't send authorization header"""

    def __init__(self, message):
        super().__init__(message)


class NewChatError(Exception):
    """Custom exception for all errors related to new chat"""

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
    chat_id: str = Field(..., description="The ID of the chat")
    mode: Mode = Field(
        ..., description="The mode of the user, either `learner` or `helper`"
    )
    prompt: Optional[str] = Field(None, description="The text prompt for the question")
    image_file: Optional[UploadFile] = Field(
        None, description="An optional image file for the question"
    )

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


## TO_BE_DELETED


class NewChatRequest(BaseModel):
    user_id: str
    mode: Mode
    language: Optional[Language] = None
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
    async def parse_new_chat_request(
            user_id: str = Form(...),
            mode: Mode = Form(...),
            language: Optional[Language] = Form(None),
            prompt: Optional[str] = Form(None),
            image_file: Optional[UploadFile] = File(None),
    ) -> "NewChatRequest":
        # Construct the NewChatRequest object
        return NewChatRequest(
            user_id=user_id,
            mode=mode,
            language=language,
            prompt=prompt,
            image_file=image_file,
        )
        # except ValidationError as e:
        #     # Handle validation errors, e.g., by raising an HTTP exception
        #     raise HTTPException(status_code=400, detail="Invalid request data")

    def to_UploadQuestionRequest(self, chat_id: str):
        return UploadQuestionRequest(
            chat_id=chat_id,
            mode=self.mode,
            prompt=self.prompt,
            image_file=self.image_file,
        )


class ChatRequest(BaseModel):
    query: Optional[str] = Field(None, description="The query text")
    chat_id: str = Field(..., description="The ID of the chat")
    language: Optional[Language] = Field(None, description="The language of the chat")


class NewChatIDRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user")


class NewChatRequest(BaseModel):
    user_id: str
    mode: Mode
    language: Optional[Language] = None
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
    async def parse_new_chat_request(
            user_id: str = Form(...),
            mode: Mode = Form(...),
            language: Optional[Language] = Form(None),
            prompt: Optional[str] = Form(None),
            image_file: Optional[UploadFile] = File(None),
    ) -> "NewChatRequest":
        # Construct the NewChatRequest object
        return NewChatRequest(
            user_id=user_id,
            mode=mode,
            language=language,
            prompt=prompt,
            image_file=image_file,
        )
        # except ValidationError as e:
        #     # Handle validation errors, e.g., by raising an HTTP exception
        #     raise HTTPException(status_code=400, detail="Invalid request data")

    def to_UploadQuestionRequest(self, chat_id: str):
        return UploadQuestionRequest(
            chat_id=chat_id,
            mode=self.mode,
            prompt=self.prompt,
            image_file=self.image_file,
        )


class NewChatResponse(BaseModel):
    chat_id: str = Field(..., description="The ID of the new chat")


class UploadQuestionResponse(BaseModel):
    chat_id: str = Field(..., description="The ID of the new chat")


class SSEResponse(BaseModel):
    event: str = Field(..., description="Events of SSE reponse.", example="type")
    data: dict = Field(..., example="""{"chat_again": BOOLEAN}""")


class ChatResponse(BaseModel):
    id: str = Field(..., description="Chat Id in UUID")
    question: Optional[str] = Field(..., description="Chat question")
    learner_mode: Optional[bool] = Field(..., description="If is learner mode")
    thumbnail_str: Optional[str] = Field(
        ..., description="Thumbnail image string in base64 format"
    )
    created_at: datetime.datetime = Field(..., description="Chat creation time")


class AllChatsResponse(BaseModel):
    data: List[ChatResponse] = Field(
        ..., example="""[{"id": "", "learner_mode": "", "question":"", ...}]"""
    )
    count: int = Field(..., description="number of chats")


class GetChatResponse(BaseModel):
    payload: Optional[Dict[str, Any]] = Field(None, description="Chat history")
    question: Optional[str] = Field(None, description="Chat question")
    image_str: Optional[str] = Field(None, description="Image string in base64 format")
    chat_again: bool = Field(..., description="Boolean if allowed to chat again")
    text_prompt: Optional[str] = Field(None, description="Chat text prompt")
    image_content: Optional[str] = Field(None, description="Chat image content")


class DeleteChatResponse(BaseModel):
    chat_id: str = Field(..., description="The ID of the deleted chat")
