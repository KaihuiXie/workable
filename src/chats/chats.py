import json
import logging
import re
import time
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from starlette.responses import StreamingResponse

from common.decorators import TimerLogLevel, timer
from src.chats.interfaces import (
    ChatOwnershipError,
    ChatRequest,
    Mode,
    UploadQuestionRequest,
)
from src.chats.supabase import ChatsSupabase
from src.math_agent.math_agent import MathAgent
from src.utils import check_message_size, preprocess_image

# Configure logging
logging.basicConfig(level=logging.INFO)


class Chat:
    def __init__(self, supabase: ChatsSupabase, math_agent: MathAgent):
        self.supabase = supabase
        self.math_agent = math_agent

    def get_new_chat_id(self, user_id: str):
        return self.supabase.create_empty_chat(
            user_id=user_id,
        )

    @timer(log_level=TimerLogLevel.BASIC)
    async def parse_question(
        self,
        request: UploadQuestionRequest = Depends(
            UploadQuestionRequest.parse_question_request
        ),
    ):
        image_string = ""
        thumbnail_string = ""
        if request.image_file:
            image_bytes = await request.image_file.read()
            image_string, thumbnail_string = preprocess_image(image_bytes)
            question = self.math_agent.parse_question(image_string, request.prompt)
        elif request.prompt:
            question = request.prompt
        else:
            raise HTTPException(
                status_code=500,
                detail=f"At least one of `image_file` or `prompt` are required!",
            )

        response = self.supabase.fulfill_empty_chat(
            chat_id=request.chat_id,
            image_str=image_string,
            thumbnail_str=thumbnail_string,
            question=question,
            is_learner_mode=(request.mode == Mode.LEARNER),
        )
        return response

    @timer(log_level=TimerLogLevel.VERBOSE)
    async def solve(self, request: ChatRequest):
        payload = {"messages": []}
        chat = self.supabase.get_chat_by_id(request.chat_id)
        language = request.language.name if request.language else None
        response = self.math_agent.solve(chat, payload["messages"], language)
        return StreamingResponse(
            self.__event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    @timer(log_level=TimerLogLevel.BASIC)
    async def chat(self, request: ChatRequest):
        payload = self.supabase.get_chat_payload_by_id(request.chat_id)
        payload["messages"].append({"role": "user", "content": request.query})
        response = self.math_agent.query(payload["messages"])
        return StreamingResponse(
            self.__event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    def get_all_chats(self, user_id: str):
        response = self.supabase.get_all_chats(user_id)
        for record in response.data:
            question = record["question"]
            match = re.search(r"<question>(.*?)</question>", question, re.DOTALL)
            if match:
                question = match.group(1)
            record["question"] = question
        # if record["question"] == "", we filter the record out
        response.data = [record for record in response.data if record["question"] != ""]
        return response

    def get_chat(self, chat_id: str, user_id: str):
        if not self.supabase.user_has_access(chat_id=chat_id, user_id=user_id):
            raise ChatOwnershipError(
                f"User {user_id} does not have access to chat {chat_id}!"
            )
        payload = self.supabase.get_chat_payload_by_id(chat_id)
        question = self.supabase.get_chat_question_by_id(chat_id)
        image_str = self.supabase.get_chat_image_by_id(chat_id)
        chat_again = ("messages" not in payload) or check_message_size(
            payload["messages"]
        )
        return {
            "payload": payload,
            "question": question,
            "image_str": image_str,
            "chat_again": chat_again,
        }

    def delete_chat(self, chat_id: str):
        self.supabase.delete_chat_by_id(chat_id)

    async def __event_generator(self, response, payload, chat_id, callback=None):
        full_response = ""
        chat_again = check_message_size(payload["messages"])
        yield f"event: type\n\n"
        yield f"data: {json.dumps({'chat_again': chat_again})}\n\n"

        yield f"event: answer\n\n"
        try:
            for event in response:
                event_text = event.choices[0].delta.content
                if event_text is not None:
                    full_response += event_text
                    event_data = {"text": event_text}
                    yield f"data: {json.dumps(event_data)}\n\n"
        except Exception as e:
            # Handle exceptions or end of stream
            logging.error(e)
            yield
        finally:
            if full_response:
                try:
                    payload["messages"].append(
                        {"role": "assistant", "content": full_response}
                    )
                    self.supabase.update_payload(chat_id, payload)
                    if callback:
                        callback()
                except Exception as db_error:
                    logging.error("Error updating payload to database: %s", db_error)
