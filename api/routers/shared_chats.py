import logging

from fastapi import APIRouter, HTTPException, Request

from common.objects import shared_chats
from src.shared_chats.interfaces import (
    DeleteSharedChatResponse,
    GetSharedChatResponse,
    NewSharedChatRequest,
    NewSharedChatResponse,
    AuthorizationError,
)

router = APIRouter(
    prefix="/shared_chat",
    tags=["shared_chat"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/create", response_model=NewSharedChatResponse)
async def create_shared_chat(request: Request, shared_chat_request: NewSharedChatRequest) -> NewSharedChatResponse:
    """
    Create a shared chat for the chat specified in the request.

    - param request: `NewSharedChatRequest`, including two fields,\n
      - `chat_id`: The chat id of the chat to be shared\n
      - `is_permanent`: Whether this shared chat should expire after the `EXPIRATION` time\n
    - return: `NewSharedChatRequest`, including one field,\n
      - `shared_chat_id`, which will be used when users want to get the shared chat\n
    """
    try:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")
        shared_chat_id = shared_chats.create_shared_chat(
            shared_chat_request, authorization)
        return NewSharedChatResponse(shared_chat_id=shared_chat_id)
    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{shared_chat_id}", response_model=GetSharedChatResponse)
async def get_shared_chat(shared_chat_id: str) -> GetSharedChatResponse:
    """
    Get a shared chat by `shared_chat_id`.\n

    - param `shared_chat_id`: Shared chat id\n
    - return: `GetSharedChatResponse` object containing fields for the shared chat snapshot, if the requested shared chat exists and doesn't expire yet. Otherwise raise `404` exception.\n
    """
    try:
        shared_chat = shared_chats.get_shared_chat(shared_chat_id)
        if shared_chat is None:
            raise HTTPException(
                status_code=404,
                detail=f"Shared chat: {shared_chat_id} doesn't exist or has expired",
            )
        return GetSharedChatResponse(shared_chat)
    except HTTPException as e:
        logging.error(e)
        raise e
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/by_shared_chat_id/{shared_chat_id}", response_model=DeleteSharedChatResponse
)
async def delete_shared_chat_by_shared_chat_id(
    shared_chat_id: str,
) -> DeleteSharedChatResponse:
    """
    Delete a shared chat by `shared_chat_id`.\n

    - param `shared_chat_id`: Shared chat id\n
    - return: a list of the IDs of the deleted shared chat.\n
    """
    try:
        response = shared_chats.delete_shared_chat_by_shared_chat_id(
            shared_chat_id)
        return DeleteSharedChatResponse(
            shared_chat_id=[chat["id"] for chat in response.data]
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/by_chat_id/{chat_id}", response_model=DeleteSharedChatResponse)
async def delete_shared_chat_by_chat_id(chat_id: str) -> DeleteSharedChatResponse:
    """
    Delete *ALL* shared chats created from the chat specified by `chat_id`.\n

    - param `chat_id`: chat id\n
    - return: a list of the IDs of the deleted shared chat.\n
    """
    try:
        response = shared_chats.delete_shared_chat_by_chat_id(chat_id)
        return DeleteSharedChatResponse(
            shared_chat_id=[chat["id"] for chat in response.data]
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
