from dotenv import load_dotenv
import yaml
import os
import json
import time

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.math_agent.math_agent import MathAgent
from src.math_agent.supabase import Supabase
from src.interfaces import (
    QuestionRequest,
    parse_question_request,
    ChatRequest,
    AllChatsRequest,
    Mode,
    UpdateCreditRequest, DecrementCreditRequest,
)
from src.middlewares import (
    ExtendTimeoutMiddleware,
    TimerMiddleware,
)
from src.utils import preprocess_image, check_message_size

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initalization
load_dotenv()
OPENAI_API_KEYS = os.getenv("OPENAI_API_KEYS")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WOLFRAM_ALPHA_APP_ID = os.getenv("WOLFRAM_ALPHA_APP_ID")
supabase = Supabase(SUPABASE_URL, SUPABASE_KEY)
math_agent = MathAgent(OPENAI_API_KEYS, WOLFRAM_ALPHA_APP_ID)

# FastAPI
app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://react-learning-app-blush.vercel.app",
        "http://react-learning-app-blush.vercel.app",
        "http://localhost:3000",
        "https://localhost:3000",
        "https://chat.mathsolver.top",
        "http://chat.mathsolver.top",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(ExtendTimeoutMiddleware)
app.add_middleware(TimerMiddleware)


@app.get("/examples")
async def get_examples():
    try:
        current_directory = os.path.dirname(os.path.realpath(__file__))
        with open(f"{current_directory}/config/example_chat_ids.yaml", "r") as file:
            example_chat_ids = yaml.safe_load(file)["chat_ids"]
            response = supabase.get_chats_by_ids(example_chat_ids)
            return {"data": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/question")
async def prepare_question(request: QuestionRequest = Depends(parse_question_request)):
    try:
        question = ""
        image_string = ""
        thumbnail_string = ""
        if request.image_file:
            image_bytes = await request.image_file.read()
            image_string, thumbnail_string = preprocess_image(image_bytes)
            question = math_agent.query_vision(image_string, request.prompt)
        elif request.prompt:
            question = request.prompt
        else:
            raise HTTPException(
                status_code=500,
                detail=f"At least one of `image_file` or `prompt` are required!",
            )
        # Upsert to db, assuming create_chat now correctly handles the parameters
        chat_id = supabase.create_chat(
            image_str=image_string,
            thumbnail_str=thumbnail_string,
            user_id=request.user_id,
            question=question,
            is_learner_mode=(request.mode == Mode.LEARNER),
        )
        return {"chat_id": chat_id, "question": question}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during reading image: {str(e)}"
        )


@app.post("/solve")
async def solve(request: ChatRequest):
    try:
        start_time = time.time()  # Record the start time
        chat_info = supabase.get_chat_by_id(request.chat_id)
        question = chat_info["question"]
        payload = {"messages": []}

        if chat_info["learner_mode"]:
            response = math_agent.learner(question, payload["messages"])
        else:
            response = math_agent.helper(question, payload["messages"])

        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time  # Calculate the time taken
        # Log or store the time taken
        print("Time taken before first reponse received:", time_taken)

        return StreamingResponse(
            event_generator(
                response, payload, request.chat_id),
            media_type="text/event-stream",
        )

    except Exception as e:
        print(e)
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Query db to get messages
        start_time0 = time.time()  # Record the start time
        payload = supabase.get_chat_payload_by_id(request.chat_id)
        payload["messages"].append({"role": "user", "content": request.query})

        start_time = time.time()  # Record the start time
        print("Getting supabase:", start_time - start_time0)

        response = math_agent.query(payload["messages"])
        end_time = time.time()  # Record the end time
        print("Chat before first reponse received:", end_time - start_time)
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
        payload = supabase.get_chat_payload_by_id(chat_id)
        # Hide the two messages
        messages = payload["messages"]
        return {"payload": messages[2:]}
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


@app.post("/credit/{user_id}")
async def create_credit(user_id: str):
    try:
        id = supabase.create_credit(user_id)
        return {"id": id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/credit/{user_id}")
async def get_credit(user_id: str):
    try:
        response = supabase.get_credit_by_user_id(user_id)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/credit/temp")
async def update_temp_credit(request: UpdateCreditRequest):
    try:
        response = supabase.update_temp_credit_by_user_id(
            request.user_id, request.credit
        )
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/credit/perm")
async def update_perm_credit(request: UpdateCreditRequest):
    try:
        response = supabase.update_perm_credit_by_user_id(
            request.user_id, request.credit
        )
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/credit")
async def decrement_credit(request: DecrementCreditRequest):
    try:
        supabase.decrement_credit(request.user_id)
        return {"decremental": True}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/referrer/{invitation_token}")
async def get_referrer(invitation_token: str):
    try:
        is_invited, referrer_id = supabase.get_referrer_id_by_invitation_token(
            invitation_token
        )
        return {"is_invited": is_invited, "referrer_id": referrer_id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/invitation/{user_id}")
async def get_invitation(user_id: str):
    try:
        response = supabase.get_invitation_by_user_id(user_id)
        return {"token": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


async def event_generator(response, payload, chat_id, callback=None):
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
            payload["messages"].append({"role": "assistant", "content": full_response})
            supabase.update_payload(chat_id, payload)
            if callback:
                callback()
    except Exception as e:
        # Handle exceptions or end of stream
        logging.error(e)
        yield
