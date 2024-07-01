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
    GetChatResponse,
    Language,
    Mode,
    NewChatRequest,
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


def replace_wolfram_url(chat):
    payload = chat["payload"]
    if (
        not chat["learner_mode"]
        and chat["wolfram_image"]
        and payload
        and "messages" in payload
    ):
        image = chat["wolfram_image"]["image"]
        url = chat["wolfram_image"]["url"]
        for message in payload["messages"]:
            if message["role"] == "assistant":
                message["content"] = message["content"].replace(url, image)
    del chat["wolfram_image"]


class Chat:
    def __init__(self, supabase: ChatsSupabase, math_agent: MathAgent):
        self.supabase = supabase
        self.math_agent = math_agent

    # TO_BE_DELETED
    def get_new_chat_id(self, user_id: str):
        return self.supabase.create_empty_chat(
            user_id=user_id,
        )

    @timer(log_level=TimerLogLevel.BASIC)
    async def parse_question(self, request: UploadQuestionRequest):
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
            columns[ChatColumn.TEXT_PROMPT] = request.prompt
        else:
            raise HTTPException(
                status_code=500,
                detail=f"At least one of `image_file` or `prompt` are required!",
            )
        columns[ChatColumn.LEARNER_MODE] = request.mode == Mode.LEARNER
        data, count = self.supabase.update_chat_columns_by_id(request.chat_id, columns)
        return data[1][0]["id"]

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

    # TO_BE_DELETED

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
        try:
            all_chats = self.supabase.get_all_chats(user_id)
            # if record["question"] == "", we filter the record out
            all_chats.data = [chat for chat in all_chats.data if chat["question"] != ""]
            return all_chats
        except Exception as e:
            print(e)
            logging.error(e)

    def get_chat(self, chat_id: str, user_id: str) -> GetChatResponse:
        if not self.supabase.user_has_access(chat_id=chat_id, user_id=user_id):
            raise ChatOwnershipError(
                f"User {user_id} does not have access to chat {chat_id}!"
            )
        chat = self.supabase.get_chat_by_id(chat_id)
        payload = chat["payload"]
        replace_wolfram_url(chat)
        chat_again = (
            not payload
            or ("messages" not in payload)
            or check_message_size(payload["messages"])
        )
        response = GetChatResponse(
            payload=payload,
            question=chat["question"],
            image_str=chat["image_str"],
            chat_again=chat_again,
            text_prompt=chat["text_prompt"],
            image_content=chat["image_content"],
        )
        return response

    def delete_chat(self, chat_id: str):
        self.supabase.delete_chat_by_id(chat_id)

    async def __event_generator(self, response, payload, chat_id, callback=None):
        full_response = ""
        try:
            chat_again = check_message_size(payload["messages"])
            yield f"event: type\n\n"
            yield f"data: {json.dumps({'chat_again': chat_again})}\n\n"
            yield f"event: answer\n\n"
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
            for event in response:
                event_text = event.choices[0].delta.content
                if event_text is not None:
                    full_response += event_text
            try:
                payload["messages"].append(
                    {"role": "assistant", "content": full_response}
                )
                self.supabase.update_payload(chat_id, payload)
                if callback:
                    callback()
            except Exception as db_error:
                logging.error("Error updating payload to database: %s", db_error)

    async def __new_chat_event_generator(
        self, response, payload, chat_id, callback=None
    ):
        full_response = ""
        try:
            yield f"event: chat_id\ndata: {json.dumps(chat_id)}\n\n"
            chat_again = check_message_size(payload["messages"])
            yield f"event: chat_again\ndata: {json.dumps(chat_again)}\n\n"
            for event in response:
                event_text = event.choices[0].delta.content
                if event_text is not None:
                    full_response += event_text
                    event_data = {"text": event_text}
                    yield f"event: answer\ndata: {json.dumps(event_data)}\n\n"
        except Exception as e:
            # Handle exceptions or end of stream
            self.delete_chat(chat_id)
            logging.error(e)
            yield
        finally:
            for event in response:
                event_text = event.choices[0].delta.content
                if event_text is not None:
                    full_response += event_text
            try:
                payload["messages"].append(
                    {"role": "assistant", "content": full_response}
                )
                self.supabase.update_payload(chat_id, payload)
                if callback:
                    callback()
            except Exception as db_error:
                self.delete_chat(chat_id)
                logging.error("Error updating payload to database: %s", db_error)

    async def __parse_question(self, request: NewChatRequest, chat_id: str):
        upload_question_request = request.to_UploadQuestionRequest(chat_id)
        await self.parse_question(upload_question_request)

    @timer(log_level=TimerLogLevel.VERBOSE)
    async def __solve(self, chat_id: str, language: Language):
        payload = {"messages": []}
        chat = self.supabase.get_chat_by_id(chat_id)
        language = language.name if language else None
        response = self.math_agent.solve(chat, payload["messages"], language)
        return StreamingResponse(
            self.__new_chat_event_generator(response, payload, chat_id),
            media_type="text/event-stream",
        )

    async def new_chat(self, request: NewChatRequest, creditService):
        creditService.decrement_credit(request.user_id)
        chat_id = self.supabase.create_empty_chat(
            user_id=request.user_id,
        )
        await self.__parse_question(request, chat_id)
        return await self.__solve(chat_id, request.language)

    async def sse_error_generator(self, error, status_code):
        yield f"event: error\ndata: {json.dumps({'error': error, 'status_code': status_code})}\n\n"

    async def sse_error(self, error, status_code):
        return StreamingResponse(
            self.sse_error_generator(error, status_code), media_type="text/event-stream"
        )
