import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse

from common.objects import chats, credits
from src.chats.interfaces import (
    AllChatsResponse,
    ChatOwnershipError,
    ChatRequest,
    DeleteChatResponse,
    GetChatResponse,
    NewChatIDRequest,
    NewChatRequest,
    NewChatResponse,
    SSEResponse,
    UploadQuestionRequest,
    UploadQuestionResponse,
)

router = APIRouter(
    # prefix="/chats",
    tags=["chats"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/new_chat_id", response_model=NewChatResponse)
async def get_new_chat_id(request: NewChatIDRequest) -> NewChatResponse:
    try:
        temp_credit, perm_credit = credits.get_credit(request.user_id)
        if temp_credit + perm_credit <= 0:
            raise ValueError("Not enough credits")
        chat_id = chats.get_new_chat_id(request.user_id)
        return NewChatResponse(chat_id=chat_id)
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
        return await chats.new_chat(request, credits)
    except ValueError:
        return await chats.sse_error("Balance is out of credits", 405)
    except Exception as e:
        return await chats.sse_error("Internet error", 500)


@router.post("/question_photo", response_model=UploadQuestionResponse)
async def upload_question_photo(
    request: UploadQuestionRequest = Depends(
        UploadQuestionRequest.parse_question_request
    ),
) -> UploadQuestionResponse:
    try:
        chat_id = await chats.parse_question(request)
        return UploadQuestionResponse(chat_id=chat_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during reading image: {str(e)}"
        )


@router.post("/solve", response_model=SSEResponse)
async def solve(request: ChatRequest):
    try:
        return await chats.solve(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=SSEResponse)
async def chat(request: ChatRequest):
    try:
        return await chats.chat(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all_chats/{user_id}", response_model=AllChatsResponse)
async def all_chats(user_id: str):
    try:
        response = chats.get_all_chats(user_id)
        return AllChatsResponse(data=response.data, count=response.count)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{chat_id}", response_model=GetChatResponse)
async def get_chat(chat_id: str, user_id: str):
    try:
        return chats.get_chat(chat_id=chat_id, user_id=user_id)
    except ChatOwnershipError as e:
        logging.error(e)
        raise HTTPException(status_code=405, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{chat_id}", response_model=DeleteChatResponse)
async def delete_chat(chat_id: str):
    try:
        chats.delete_chat(chat_id)
        return DeleteChatResponse(chat_id=chat_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
