import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from common.objects import chats, credits, io_thread_pool
from src.chats.interfaces import (
    AllChatsResponse,
    AuthorizationError,
    ChatOwnershipError,
    ChatRequest,
    DeleteChatResponse,
    GetChatResponse,
    NewChatError,
    NewChatRequest,
    SSEResponse,
)

router = APIRouter(
    # prefix="/chats",
    tags=["chats"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/new_chat")
def new_chat(
    request: Request,
    chat_request: NewChatRequest = Depends(NewChatRequest.parse_new_chat_request),
):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")
        temp_credit, perm_credit = credits.get_credit(chat_request.user_id)
        if temp_credit + perm_credit <= 0:
            raise ValueError("Not enough credits")
        return chats.new_chat(
            chat_request, credits, io_thread_pool, authorization.replace("Bearer ", "")
        )
    except NewChatError as e:
        return chats.sync_sse_error(f"{e}", 441)
    except ValueError:
        return chats.sync_sse_error("Balance is out of credits", 405)
    except AuthorizationError as e:
        return chats.sync_sse_error(e, 401)
    except Exception as e:
        return chats.sync_sse_error(f"Internet error + {e}", 500)

@router.post("/chat", response_model=SSEResponse)
def chat(chat_request: ChatRequest, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")

        return chats.chat(chat_request, authorization.replace("Bearer ", ""))
    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all_chats/{user_id}", response_model=AllChatsResponse)
def all_chats(user_id: str, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")
        response = chats.get_all_chats(user_id, authorization.replace("Bearer ", ""))
        return AllChatsResponse(data=response.data, count=response.count)
    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{chat_id}", response_model=GetChatResponse)
def get_chat(chat_id: str, user_id: str, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")

        return chats.get_chat(
            chat_id=chat_id,
            user_id=user_id,
            auth_token=authorization.replace("Bearer ", ""),
        )
    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ChatOwnershipError as e:
        logging.error(e)
        raise HTTPException(status_code=405, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{chat_id}", response_model=DeleteChatResponse)
def delete_chat(chat_id: str, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")

        chats.delete_chat(chat_id, authorization.replace("Bearer ", ""))
        return DeleteChatResponse(chat_id=chat_id)
    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# TODO deprecated
# @router.post("/new_chat_id", response_model=NewChatResponse)
# async def get_new_chat_id(
#     chat_request: NewChatIDRequest, request: Request
# ) -> NewChatResponse:
#     try:
#         # get the authorization header
#         authorization = request.headers.get("Authorization")
#         if not authorization:
#             raise AuthorizationError("Authorization header missing")

#         temp_credit, perm_credit = credits.get_credit(chat_request.user_id)
#         if temp_credit + perm_credit <= 0:
#             raise ValueError("Not enough credits")

#         chat_id = chats.get_new_chat_id(
#             chat_request.user_id, authorization.replace("Bearer ", "")
#         )
#         return NewChatResponse(chat_id=chat_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=405,
#             detail=f"User: {chat_request.user_id} doesn't have enough credits to create a new chat",
#         )
#     except AuthorizationError as e:
#         raise HTTPException(status_code=401, detail=str(e))
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )


# @router.post("/new_chat")
# async def new_chat(
#     request: Request,
#     chat_request: NewChatRequest = Depends(NewChatRequest.parse_new_chat_request),
# ):
#     try:
#         # get the authorization header
#         authorization = request.headers.get("Authorization")
#         if not authorization:
#             raise AuthorizationError("Authorization header missing")
#         temp_credit, perm_credit = credits.get_credit(chat_request.user_id)
#         if temp_credit + perm_credit <= 0:
#             raise ValueError("Not enough credits")
#         return await chats.new_chat(
#             chat_request, credits, io_thread_pool, authorization.replace("Bearer ", "")
#         )
#     except NewChatError as e:
#         return await chats.sse_error(f"{e}", 441)
#     except ValueError:
#         return await chats.sse_error("Balance is out of credits", 405)
#     except AuthorizationError as e:
#         return await chats.sse_error(e, 401)
#     except Exception as e:
#         return await chats.sse_error(f"Internet error + {e}", 500)

# @router.post("/question_photo", response_model=UploadQuestionResponse)
# async def upload_question_photo(
#     request: Request,
#     chat_request: UploadQuestionRequest = Depends(
#         UploadQuestionRequest.parse_question_request
#     ),
# ) -> UploadQuestionResponse:
#     try:
#         # get the authorization header
#         authorization = request.headers.get("Authorization")
#         if not authorization:
#             raise AuthorizationError("Authorization header missing")

#         chat_id = await chats.parse_question(
#             chat_request, authorization.replace("Bearer ", "")
#         )
#         return UploadQuestionResponse(chat_id=chat_id)
#     except AuthorizationError as e:
#         raise HTTPException(status_code=401, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/solve", response_model=SSEResponse)
# async def solve(chat_request: ChatRequest, request: Request):
#     try:
#         # get the authorization header
#         authorization = request.headers.get("Authorization")
#         if not authorization:
#             raise AuthorizationError("Authorization header missing")

#         return await chats.solve(chat_request, authorization.replace("Bearer ", ""))
#     except AuthorizationError as e:
#         raise HTTPException(status_code=401, detail=str(e))
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))
