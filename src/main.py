from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Callable
import logging


import os
import json
from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.interfaces import QuestionRequest, ChatRequest, AllChatsRequest
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


@app.post("/image/")
async def read_image(request: QuestionRequest):
    try:
        question = math_agent.query_vision(request.image_string)
        # Upsert to db, assuming create_chat now correctly handles the parameters
        chat_id = supabase.create_chat(request.image_string, request.user_id, question)
        return {"chat_id": chat_id, "status_code": 200}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during reading image: {str(e)}"
        )


@app.post("/helper/")
async def helper(request: ChatRequest):
    try:
        question = supabase.get_chat_question_by_id(request.chat_id)
        payload = Supabase.question_to_payload(question)
        response = math_agent.helper(payload["messages"])
        return StreamingResponse(
            event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/learner/")
async def learner(request: ChatRequest):
    try:
        question = supabase.get_chat_question_by_id(request.chat_id)
        payload = Supabase.question_to_payload(question)
        response = math_agent.learner(payload["messages"])

        return StreamingResponse(
            event_generator(response, payload, request.chat_id),
            media_type="text/event-stream",
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/")
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


@app.post("/all-chats/")
async def all_chats(request: AllChatsRequest):
    try:
        # Query db to get messages
        response = supabase.get_all_chats(request.user_id)
        return {"data": response, "status_code": 200}
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
