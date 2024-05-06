import logging

from fastapi import HTTPException, APIRouter, Depends

from common.object import chats
from src.chats.interfaces import (
    UploadQuestionRequest,
    NewChatRequest,
    ChatRequest,
)

router = APIRouter(
    # prefix="/chats",
    tags=["chats"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/new_chat_id")
async def get_new_chat_id(request: NewChatRequest):
    try:
        chat_id = chats.get_new_chat_id(request.user_id)
        return {"chat_id": chat_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during creating new chat id: {str(e)}",
        )


@router.post("/question_photo")
async def upload_question_photo(
    request: UploadQuestionRequest = Depends(
        UploadQuestionRequest.parse_question_request
    ),
):
    try:
        return await chats.upload_question_photo(request)
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
async def get_chat(chat_id: str):
    try:
        return chats.get_chat(chat_id)
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
