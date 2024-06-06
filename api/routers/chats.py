import logging

from fastapi import APIRouter, Depends, HTTPException

from common.objects import chats, credits
from src.chats.interfaces import (
    ChatOwnershipError,
    ChatRequest,
    NewChatIDRequest,
    NewChatRequest,
    UploadQuestionRequest,
)

router = APIRouter(
    # prefix="/chats",
    tags=["chats"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/new_chat_id")
async def get_new_chat_id(request: NewChatIDRequest):
    try:
        temp_credit, perm_credit = credits.get_credit(request.user_id)
        if temp_credit + perm_credit <= 0:
            raise ValueError("Not enough credits")
        chat_id = chats.get_new_chat_id(request.user_id)
        return {"chat_id": chat_id}
    except ValueError:
        raise HTTPException(
            status_code=405,
            detail=f"User: {request.user_id} doesn't have enough credits to create a new chat",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during creating new chat id: {str(e)}",
        )


@router.post("/new_chat")
async def new_chat(
    request: NewChatRequest = Depends(NewChatRequest.parse_new_chat_request),
):
    try:
        temp_credit, perm_credit = credits.get_credit(request.user_id)
        if temp_credit + perm_credit <= 0:
            raise ValueError("Not enough credits")
        return await chats.new_chat(request)
    except ValueError:
        raise HTTPException(
            status_code=405,
            detail=f"User: {request.user_id} doesn't have enough credits to create a new chat",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/question_photo")
async def upload_question_photo(
    request: UploadQuestionRequest = Depends(
        UploadQuestionRequest.parse_question_request
    ),
):
    try:
        return await chats.parse_question(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during reading image: {str(e)}"
        )


@router.post("/solve")
async def solve(request: ChatRequest):
    try:
        return await chats.solve(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        return await chats.chat(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all_chats/{user_id}")
async def all_chats(user_id: str):
    try:
        return chats.get_all_chats(user_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{chat_id}")
async def get_chat(chat_id: str, user_id: str):
    try:
        return chats.get_chat(chat_id=chat_id, user_id=user_id)
    except ChatOwnershipError as e:
        logging.error(e)
        raise HTTPException(status_code=405, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str):
    try:
        chats.delete_chat(chat_id)
        return {"message": f"Chat {chat_id} deleted successfully"}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
