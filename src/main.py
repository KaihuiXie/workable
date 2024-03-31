from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Callable
import logging


import os
import json
from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.interfaces import (
    QuestionRequest,
    ChatRequest,
    AllChatsRequest,
    Mode,
    SignUpRequest,
    SignInRequest,
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


def set_no_cache_headers(response: Response) -> Response:
    response.headers["Potato"] = "potato"
    return response


@app.post("/sign_up")
async def sign_up(request: SignUpRequest):
    try:
        res = supabase.sign_up(request.email, request.password)
        return res
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sign_in")
async def sign_in(request: SignInRequest):
    try:
        res = supabase.sign_in_with_password(
            email=request.email,
            password=request.password,
        )
        return res
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# OAuth
@app.get("/oauth/google")
async def signin_with_google(request):
    res = supabase.auth().sign_in_with_oauth(
        {
            "provider": "google",
            "options": {"redirect_to": f"{request.redirect_to}/callback"},
        }
    )
    return RedirectResponse(url=res.url)


@app.get("/oauth/apple")
async def signin_with_apple(request):
    res = supabase.auth().sign_in_with_oauth(
        {
            "provider": "apple",
            "options": {"redirect_to": f"{request.redirect_to}/callback"},
        }
    )
    return RedirectResponse(url=res.url)


@app.get("/callback")
async def callback(request: Request, next: str = "/"):
    code = request.query_params.get("code")

    if code:
        res = supabase.auth().exchange_code_for_session({"auth_code": code})
        return RedirectResponse(url=next)
    else:
        raise HTTPException(status_code=400, detail="Authorization code not found")


@app.post("/sign_out")
async def sign_out():
    try:
        res = supabase.sign_out()
        return "success"
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user")
async def get_user():
    try:
        user = supabase.get_user()
        return user
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


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
        return {"chat_id": chat_id}
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
