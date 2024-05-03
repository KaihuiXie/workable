from dotenv import load_dotenv
import yaml
import os
import json
import time
import re

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from common.object import supabase, math_agent
from api.routers import shared_chats
from src.interfaces import (
    UploadQuestionRequest,
    parse_question_request,
    ChatRequest,
    AllChatsRequest,
    Mode,
    UpdateCreditRequest,
    DecrementCreditRequest,
    Language,
    SignInRequest,
    OAuthSignInRequest,
    SignUpRequest,
)
from src.middlewares import (
    ExtendTimeoutMiddleware,
    TimerMiddleware,
)
from src.utils import preprocess_image, check_message_size

# Configure logging
logging.basicConfig(level=logging.INFO)

tags_metadata = [
    {
        "name": "shared_chat",
        "description": "Operations with sharing chat.",
    },
]

# FastAPI
app = FastAPI(openapi_tags=tags_metadata)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://react-learning-app-blush.vercel.app",
        "http://react-learning-app-blush.vercel.app",
        "https://react-learning-app-u7tw.vercel.app",
        "http://react-learning-app-u7tw.vercel.app",
        "https://uat-cqomi71sh-asian-math-top.vercel.app",
        "https://uat-asian-math-top.vercel.app/",
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
app.include_router(shared_chats.router)


@app.get("/health")
async def health_check():
    try:
        return {"status": "up"}
    except Exception as e:
        logging.error(f"Health Check Failed: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable")


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


@app.get("/new_chat_id/{user_id}")
async def get_new_chat_id(user_id: str):
    try:
        chat_id = supabase.create_empty_chat(
            user_id=user_id,
        )
        return {"chat_id": chat_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during creating new chat id: {str(e)}",
        )


@app.post("/question_photo")
async def upload_question_photo(
    request: UploadQuestionRequest = Depends(parse_question_request),
):
    ## TO_BE_DELETED
    start_time = time.time()
    ## TO_BE_DELETED

    try:
        image_string = ""
        thumbnail_string = ""
        if request.image_file:
            image_bytes = await request.image_file.read()
            image_string, thumbnail_string = preprocess_image(image_bytes)

            ## TO_BE_DELETED
            start_time1 = time.time()
            print("Prerocessing image took:", start_time1 - start_time)
            ## TO_BE_DELETED

            question = math_agent.query_vision(image_string, request.prompt)

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

        response = supabase.fulfill_empty_chat(
            chat_id=request.chat_id,
            image_str=image_string,
            thumbnail_str=thumbnail_string,
            question=question,
            is_learner_mode=(request.mode == Mode.LEARNER),
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during reading image: {str(e)}"
        )


@app.post("/solve")
async def solve(request: ChatRequest):
    try:
        ## TO_BE_DELETED
        start_time = time.time()  # Record the start time
        print(
            "Solve request received:",
            time.asctime(time.localtime(start_time)),
        )
        ## TO_BE_DELETED

        chat_info = supabase.get_chat_by_id(request.chat_id)
        question = chat_info["question"]
        payload = {"messages": []}
        language = None
        if request.language:
            language = request.language.name
        if chat_info["learner_mode"]:
            response = math_agent.learner(question, payload["messages"], language)
        else:
            response = math_agent.helper(question, payload["messages"], language)

        ## TO_BE_DELETED
        print("Time taken before first reponse received:", time.time() - start_time)
        ## TO_BE_DELETED
        return StreamingResponse(
            event_generator(response, payload, request.chat_id),
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
        ## TO_BE_DELETED
        start_time = time.time()  # Record the start time
        ## TO_BE_DELETED

        payload = supabase.get_chat_payload_by_id(request.chat_id)
        payload["messages"].append({"role": "user", "content": request.query})

        response = math_agent.query(payload["messages"])

        ## TO_BE_DELETED
        print(
            f"Chat {request.chat_id} before first reponse received:",
            time.time() - start_time,
        )
        ## TO_BE_DELETED

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
        for record in response.data:
            question = record["question"]
            match = re.search(r"<question>(.*?)</question>", question, re.DOTALL)
            if match:
                question = match.group(1)
            record["question"] = question
        return {"data": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    try:
        payload = supabase.get_chat_payload_by_id(chat_id)
        question = supabase.get_chat_question_by_id(chat_id)
        image_str = supabase.get_chat_Qimage_by_id(chat_id)
        # Hide the two messages
        # messages = payload["messages"]
        return {"payload": payload, "question":question, "image_str":image_str}
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
        temp_credit = supabase.get_temp_credit_by_user_id(user_id)
        perm_credit = supabase.get_perm_credit_by_user_id(user_id)
        return {"temp_credit": temp_credit, "perm_credit": perm_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/credit/temp/{user_id}")
async def get_temp_credit(user_id: str):
    try:
        response = supabase.get_temp_credit_by_user_id(user_id)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/credit/perm/{user_id}")
async def get_perm_credit(user_id: str):
    try:
        response = supabase.get_perm_credit_by_user_id(user_id)
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


@app.post("/signup")
async def signup(request: SignUpRequest):
    try:
        auth_response = supabase.sign_up(request.email, request.phone, request.password)
        return {"auth_response": auth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
async def login(request: SignInRequest):
    try:
        auth_response = supabase.sign_in_with_password(
            request.email, request.phone, request.password
        )
        user_id = auth_response.user.id
        temp_credit = supabase.get_temp_credit_by_user_id(user_id)
        perm_credit = supabase.get_perm_credit_by_user_id(user_id)
        return {
            "auth_response": auth_response,
            "temp_credit": temp_credit,
            "perm_credit": perm_credit,
        }
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logout")
async def logout():
    try:
        auth_response = supabase.sign_out()
        return {"auth_response": auth_response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login/oauth")
async def login_oauth(request: OAuthSignInRequest):
    try:
        oauth_response = supabase.sign_in_with_oauth(request.provider)
        return {
            "oauth_response": oauth_response,
        }
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session")
async def get_session():
    try:
        session = supabase.get_session()
        return {"session": session}
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
