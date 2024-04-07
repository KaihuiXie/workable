from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Callable
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

import os
import json
from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.interfaces import (
    QuestionRequest,
    ChatRequest,
    AllChatsRequest,
    Mode,
)
from dotenv import load_dotenv

# Configure logging at the top of your test file
logging.basicConfig(level=logging.info)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = Supabase(SUPABASE_URL, SUPABASE_KEY)
math_agent = MathAgent(OPENAI_API_KEY)

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


app.add_middleware(TimerMiddleware)


@app.post("/image")
async def read_image(request: QuestionRequest):
    try:
        question = math_agent.query_vision(request.image_string)
        # Upsert to db, assuming create_chat now correctly handles the parameters
        chat_id = supabase.create_chat(
            request.image_string,
            request.user_id,
            question,
            request.mode == Mode.LEARNER,
        )
        return {"chat_id": chat_id, "question": question}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during reading image: {str(e)}"
        )


@app.post("/helper")
async def helper(request: ChatRequest):
    try:
        question = supabase.get_chat_question_by_id(request.chat_id)
        payload = Supabase.question_to_payload(question)
        response = math_agent.helper(payload["messages"])

        # decrement credit for user
        user_id = supabase.get_user_id_by_chat_id(request.chat_id)
        supabase.decrement_credit(user_id)

        return StreamingResponse(
            event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/learner")
async def learner(request: ChatRequest):
    try:
        question = supabase.get_chat_question_by_id(request.chat_id)
        payload = Supabase.question_to_payload(question)
        response = math_agent.learner(payload["messages"])

        # decrement credit for user
        user_id = supabase.get_user_id_by_chat_id(request.chat_id)
        supabase.decrement_credit(user_id)

        return StreamingResponse(
            event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Query db to get messages
        payload = supabase.get_chat_payload_by_id(request.chat_id)
        payload["messages"].append({"role": "user", "content": request.query})

        response = math_agent.query(payload["messages"])

        return StreamingResponse(
            event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/all_chats")
async def all_chats(request: AllChatsRequest):
    try:
        # Query db to get messages
        response = supabase.get_all_chats(request.user_id)
        return {"data": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_chat")
async def get_chat(chat_id: str):
    try:
        # Query db to get messages
        response = supabase.get_chat_payload_by_id(chat_id)
        return {"payload": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_credit")
async def get_credit(user_id: str):
    try:
        response = supabase.get_credit_by_id(user_id)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/temp_credit")
async def temp_credit(user_id: str, credit: int):
    try:
        response = supabase.update_temp_credit(user_id, credit)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/perm_credit")
async def perm_credit(user_id: str, credit: int):
    try:
        response = supabase.update_perm_credit(user_id, credit)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


async def event_generator(response, payload, chat_id):
    full_response = ""
    try:
        for event in response:
            event_text = event.choices[0].delta.content
            if event_text is not None:
                full_response += event_text
                event_data = {"text": event_text}
                yield f"data: {json.dumps(event_data)}\n\n"
        print(full_response)
        payload["messages"].append({"role": "assistant", "content": full_response})
        supabase.update_payload(chat_id, payload)
    except Exception as e:
        # Handle exceptions or end of stream
        logging.error(e)
        yield
