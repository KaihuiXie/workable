import json
import logging
import re
import time
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from starlette.responses import StreamingResponse

from src.chats.interfaces import ChatRequest, Mode, UploadQuestionRequest
from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.utils import check_message_size, preprocess_image

# Configure logging
logging.basicConfig(level=logging.INFO)


class Chat:
    def __init__(self, supabase: Supabase, math_agent: MathAgent):
        self.supabase = supabase
        self.math_agent = math_agent

    def get_new_chat_id(self, user_id: str):
        return self.supabase.create_empty_chat(
            user_id=user_id,
        )

    async def upload_question_photo(
        self,
        request: UploadQuestionRequest = Depends(
            UploadQuestionRequest.parse_question_request
        ),
    ):
        ## TO_BE_DELETED
        start_time = time.time()
        ## TO_BE_DELETED

        image_string = ""
        thumbnail_string = ""
        if request.image_file:
            image_bytes = await request.image_file.read()
            image_string, thumbnail_string = preprocess_image(image_bytes)

            ## TO_BE_DELETED
            start_time1 = time.time()
            print("Prerocessing image took:", start_time1 - start_time)
            ## TO_BE_DELETED

            question = self.math_agent.query_vision(image_string, request.prompt)

            ## TO_BE_DELETED
            print("query_vision image took:", time.time() - start_time1)
            ## TO_BE_DELETED

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

    async def solve(self, request: ChatRequest):
        ## TO_BE_DELETED
        start_time = time.time()  # Record the start time
        print(
            "Solve request received:",
            time.asctime(time.localtime(start_time)),
        )
        ## TO_BE_DELETED

        chat_info = self.supabase.get_chat_by_id(request.chat_id)
        question = chat_info["question"]
        payload = {"messages": []}
        language = None
        if request.language:
            language = request.language.name
        if chat_info["learner_mode"]:
            response = self.math_agent.learner(question, payload["messages"], language)
        else:
            response = self.math_agent.helper(question, payload["messages"], language)

        ## TO_BE_DELETED
        print("Time taken before first reponse received:", time.time() - start_time)
        ## TO_BE_DELETED
        return StreamingResponse(
            self.__event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    async def chat(self, request: ChatRequest):
        # Query db to get messages
        ## TO_BE_DELETED
        start_time = time.time()  # Record the start time
        ## TO_BE_DELETED

        payload = self.supabase.get_chat_payload_by_id(request.chat_id)
        payload["messages"].append({"role": "user", "content": request.query})

        response = self.math_agent.query(payload["messages"])

        ## TO_BE_DELETED
        print(
            f"Chat {request.chat_id} before first reponse received:",
            time.time() - start_time,
        )
        ## TO_BE_DELETED

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
        return response

    def get_chat(self, chat_id: str):
        payload = self.supabase.get_chat_payload_by_id(chat_id)
        question = self.supabase.get_chat_question_by_id(chat_id)
        image_str = self.supabase.get_chat_image_by_id(chat_id)
        return {"payload": payload, "question": question, "image_str": image_str}

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
            logging.info(full_response)
            if full_response:
                payload["messages"].append(
                    {"role": "assistant", "content": full_response}
                )
                self.supabase.update_payload(chat_id, payload)
                if callback:
                    callback()
        except Exception as e:
            # Handle exceptions or end of stream
            logging.error(e)
            yield
