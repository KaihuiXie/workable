import json
import logging
import re
import time
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from starlette.responses import StreamingResponse

from common.decorators import TimerLogLevel, timer
from src.chats.interfaces import (
    ChatColumn,
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


def search(content: str, tag: str):
    pattern = rf"<{tag}>((.|[\r\n])*?)</{tag}>"
    match = re.search(pattern, content, re.DOTALL)
    if match and match.group(1) != "None":
        return match.group(1)
    return None


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
        columns = dict()

        if request.image_file:
            image_bytes = await request.image_file.read()
            (
                columns[ChatColumn.IMAGE_STR],
                columns[ChatColumn.THUMBNAIL_STR],
            ) = preprocess_image(image_bytes)
            parse_result = self.math_agent.parse_question(
                columns[ChatColumn.IMAGE_STR], request.prompt
            )
            columns[ChatColumn.PAYLOAD] = {
                "messages": [{"role": "assistant", "content": parse_result}]
            }
            columns[ChatColumn.QUESTION] = search(parse_result, "question")
            image_content = search(parse_result, "image_content")
            if image_content:
                columns[ChatColumn.IMAGE_CONTENT] = image_content

            columns[ChatColumn.TEXT_PROMPT] = request.prompt
            wolfram_query = search(parse_result, "wolfram_query")
            if wolfram_query:
                columns[ChatColumn.WOLFRAM_QUERY] = wolfram_query
        elif request.prompt:
            columns[ChatColumn.QUESTION] = request.prompt
        else:
            raise HTTPException(
                status_code=500,
                detail=f"At least one of `image_file` or `prompt` are required!",
            )
        columns[ChatColumn.LEARNER_MODE] = request.mode == Mode.LEARNER
        response = self.supabase.update_chat_columns_by_id(request.chat_id, columns)
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
        payload = self.supabase.get_chat_column_by_id(
            request.chat_id, ChatColumn.PAYLOAD
        )
        payload["messages"].append({"role": "user", "content": request.query})
        response = self.math_agent.query(payload["messages"])
        return StreamingResponse(
            self.__event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    def get_all_chats(self, user_id: str):
        columns = [
            ChatColumn.ID,
            ChatColumn.THUMBNAIL_STR,
            ChatColumn.QUESTION,
            ChatColumn.LEARNER_MODE,
            ChatColumn.CREATED_AT,
            ChatColumn.TEXT_PROMPT,
        ]
        all_chats = self.supabase.get_all_chats_columns_by_user_id(user_id, columns)
        # if record["question"] == "", we filter the record out
        all_chats.data = [chat for chat in all_chats.data if chat["question"] != ""]
        return all_chats

    def get_chat(self, chat_id: str, user_id: str):
        if not self.supabase.user_has_access(chat_id=chat_id, user_id=user_id):
            raise ChatOwnershipError(
                f"User {user_id} does not have access to chat {chat_id}!"
            )
        chat = self.supabase.get_chat_by_id(chat_id)
        payload = chat["payload"]
        chat_again = (
            not payload
            or ("messages" not in payload)
            or check_message_size(payload["messages"])
        )
        chat["chat_again"] = chat_again
        return chat

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
