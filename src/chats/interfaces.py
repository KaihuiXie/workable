from enum import Enum
from fastapi import UploadFile, Form, HTTPException, File
from pydantic import BaseModel, model_validator, ValidationError
from typing import Optional

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


class Language(Enum):
    ENGLISH = "EN"
    SPANISH = "ES"
    FRENCH = "FR"
    GERMAN = "DE"
    CHINESE = "ZH"
    JAPANESE = "JA"

    @staticmethod
    def from_string(s):
        if s is None:
            return Language.ENGLISH
        try:
            return Language[s.upper()]
        except KeyError:
            raise ValueError(f"{s} is not a valid Language")


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
