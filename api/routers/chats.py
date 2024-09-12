import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from common.objects import chats, credits, users
from src.chats.interfaces import (
    ChatColumn,
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
from src.utils import is_valid_jwt_format

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
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        auth_token = authorization.replace("Bearer ", "")
        user_id = users.verify_jwt(auth_token).user.id
        temp_credit, perm_credit = credits.get_credit(user_id)
        is_premium = users.get_subscription(user_id)
        if temp_credit + perm_credit <= 0 and not is_premium:
            raise ValueError("Not enough credits")
        callback = lambda: credits.decrement_credit(user_id)
        if is_premium:
            callback = None
        return chats.new_chat(
            user_id, chat_request, callback, auth_token
        )
    except NewChatError as e:
        logging.error(e)
        return chats.sync_sse_error(f"{e}", 441)
    except ValueError as e:
        logging.error(e)
        return chats.sync_sse_error("Balance is out of credits", 405)
    except AuthorizationError as e:
        logging.error(e)
        return chats.sync_sse_error(e, 401)
    except Exception as e:
        logging.error(e)
        return chats.sync_sse_error(f"Internet error + {e}", 500)

@router.post("/chat", response_model=SSEResponse)
def chat(chat_request: ChatRequest, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        auth_token = authorization.replace("Bearer ", "")
        chat_record = chats.supabase.get_all_chat_columns_by_id(
            chat_request.chat_id, [ChatColumn.PAYLOAD, ChatColumn.LEARNER_MODE, ChatColumn.USER_ID], auth_token
        )
        user_id = users.verify_jwt(auth_token).user.id
        is_premium = users.get_subscription(user_id)
        temp_credit, perm_credit = credits.get_credit(user_id)
        callback = lambda: credits.decrement_credit(chat_record[ChatColumn.USER_ID])
        if not chat_record[ChatColumn.LEARNER_MODE]:
            if temp_credit + perm_credit <= 0 and not is_premium:
                raise ValueError("Not enough credits")
            if is_premium:
                callback = None
        else:
            callback = None
        return chats.chat(chat_request, chat_record, callback)
    except NewChatError as e:
        logging.error(e)
        return chats.sync_sse_error(f"{e}", 441)
    except ValueError as e:
        logging.error(e)
        return chats.sync_sse_error("Balance is out of credits", 405)
    except AuthorizationError as e:
        logging.error(e)
        return chats.sync_sse_error(e, 401)
    except Exception as e:
        logging.error(e)
        return chats.sync_sse_error(f"Internet error + {e}", 500)


@router.get("/all_chats", response_model=AllChatsResponse)
def all_chats(request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        try:
            user_id = users.verify_jwt(authorization.replace("Bearer ", "")).user.id
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        response = chats.get_all_chats(user_id, authorization.replace("Bearer ", ""))
        return AllChatsResponse(data=response.data, count=response.count)
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/{chat_id}", response_model=GetChatResponse)
def get_chat(chat_id: str, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        try:
            user_id = users.verify_jwt(authorization.replace("Bearer ", "")).user.id
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        return chats.get_chat(
            chat_id=chat_id,
            user_id=user_id,
            auth_token=authorization.replace("Bearer ", ""),
        )
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/chat/{chat_id}", response_model=DeleteChatResponse)
def delete_chat(chat_id: str, request: Request):
    try:
        # get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if not is_valid_jwt_format(authorization.replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Authorization not valid")
        try:
            users.verify_jwt(authorization.replace("Bearer ", ""))
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        chats.delete_chat(chat_id, authorization.replace("Bearer ", ""))
        return DeleteChatResponse(chat_id=chat_id)
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
