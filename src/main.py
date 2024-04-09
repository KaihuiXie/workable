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

# Configure logging
logging.basicConfig(level=logging.info)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WOLFRAM_ALPHA_APP_ID = os.getenv("WOLFRAM_ALPHA_APP_ID")
supabase = Supabase(SUPABASE_URL, SUPABASE_KEY)
math_agent = MathAgent(OPENAI_API_KEY, WOLFRAM_ALPHA_APP_ID)

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


@app.post("/question")
async def prepare_question(request: QuestionRequest):
    try:
        question = ""
        if request.image_string:
            question = math_agent.query_vision(request.image_string)
            if request.prompt:
                question += f"\n Instruction: {request.prompt}"
        elif request.prompt:
            question = request.prompt
        else:
            raise HTTPException(
                status_code=500,
                detail=f"At least one of `image_string` or `prompt` are required!",
            )
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


@app.post("/solve")
async def solve(request: ChatRequest):
    try:
        chat_info = supabase.get_chat_by_id(request.chat_id)
        question = chat_info["question"]
        payload = {"messages": []}

        if chat_info["learner_mode"]:
            response = math_agent.learner(question, payload["messages"])
        else:
            response = math_agent.helper(question, payload["messages"])

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
        response = supabase.get_all_chats(request.user_id)
        return {"data": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    try:
        response = supabase.get_chat_payload_by_id(chat_id)
        return {"payload": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_credit")
async def get_credit(user_id: str):
    try:
        response = supabase.get_credit_by_user_id(user_id)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/temp_credit")
async def temp_credit(user_id: str, credit: int):
    try:
        response = supabase.update_temp_credit_by_user_id(user_id, credit)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/perm_credit")
async def perm_credit(user_id: str, credit: int):
    try:
        response = supabase.update_perm_credit_by_user_id(user_id, credit)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str):
    try:
        response = supabase.delete_chat_by_id(chat_id)
        return {"message": f"Chat {chat_id} deleted successfully"}
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
        logging.info(full_response)
        # print(full_response)
        payload["messages"].append({"role": "assistant", "content": full_response})
        supabase.update_payload(chat_id, payload)
    except Exception as e:
        # Handle exceptions or end of stream
        logging.error(e)
        yield
