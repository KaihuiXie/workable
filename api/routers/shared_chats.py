import logging

from fastapi import HTTPException, APIRouter
from common.object import shared_chats
from src.shared_chats.interfaces import (
    CreateSharedChatRequest,
)

router = APIRouter(
    prefix="/shared_chat",
    tags=["shared_chat"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/create")
async def create_shared_chat(request: CreateSharedChatRequest):
    """
    Create a shared chat for the chat specified in the request.

    - param request: `CreateSharedChatRequest`, including two fields,\n
      - `chat_id`: The chat id of the chat to be shared\n
      - `is_permanent`: Whether this shared chat should expire after the `EXPIRATION` time\n
    - return: `shared_chat_id`, which will be used when users want to get the shared chat\n
    """
    try:
        return shared_chats.create_shared_chat(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{shared_chat_id}")
async def get_shared_chat(shared_chat_id: str):
    """
    Get a shared chat by `shared_chat_id`.\n

    - param `shared_chat_id`: Shared chat id\n
    - return: a json object containing all fields for the shared chat, if the requested shared chat exists and doesn't expire yet. Otherwise return `null`.\n
    """
    try:
        return shared_chats.get_shared_chat(shared_chat_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/by_shared_chat_id/{shared_chat_id}")
async def delete_shared_chat_by_shared_chat_id(shared_chat_id: str):
    """
    Delete a shared chat by `shared_chat_id`.\n

    - param `shared_chat_id`: Shared chat id\n
    - return: status of the deleting operation.\n
    """
    try:
        return shared_chats.delete_shared_chat_by_shared_chat_id(shared_chat_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/by_chat_id/{chat_id}")
async def delete_shared_chat_by_chat_id(chat_id: str):
    """
    Delete *ALL* shared chats created from the chat specified by `chat_id`.\n

    - param `chat_id`: chat id\n
    - return: status of the deleting operation.\n
    """
    try:
        return shared_chats.delete_shared_chat_by_chat_id(chat_id)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
