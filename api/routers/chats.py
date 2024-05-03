import json
import logging
import re
import time

from fastapi import HTTPException, APIRouter, Depends
from starlette.responses import StreamingResponse

from common.object import supabase, math_agent
from src.interfaces import (
    UploadQuestionRequest,
    AllChatsRequest,
    parse_question_request,
    Mode,
    ChatRequest,
)
from src.utils import check_message_size, preprocess_image

router = APIRouter(
    # prefix="/chats",
    tags=["chats"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.get("/new_chat_id/{user_id}")
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


@router.post("/question_photo")
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


@router.post("/solve")
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


@router.post("/chat")
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


@router.post("/all_chats")
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


@router.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    try:
        payload = supabase.get_chat_payload_by_id(chat_id)
        question = supabase.get_chat_question_by_id(chat_id)
        image_str = supabase.get_chat_image_by_id(chat_id)
        # Hide the two messages
        # messages = payload["messages"]
        return {"payload": payload, "question": question, "image_str": image_str}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str):
    try:
        response = supabase.delete_chat_by_id(chat_id)
        return {"message": f"Chat {chat_id} deleted successfully"}
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
