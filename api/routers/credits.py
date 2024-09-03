import logging

from fastapi import APIRouter, HTTPException, Request

from common.objects import credits, users
from src.credits.interfaces import (
    CreditResponse,
    PermCreditResponse,
    TempCreditResponse,
)

from src.chats.interfaces import (
    AuthorizationError,
)

router = APIRouter(
    prefix="/credit",
    tags=["credits"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)

@router.get("", response_model=CreditResponse)
def get_credit(request: Request) -> CreditResponse:
    """
    Get the temp and perm credits from a specific user.

    - param request: `user_id` type of string. The unique uuid of the user,\n
    - return: `temp_credit` and `perm_credit` in an array with index 0 is temp_credit, 1 is perm_credit.\n
    """
    try:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise AuthorizationError("Authorization header missing")
        auth_token = authorization.replace("Bearer ", "")
        user_id = users.verify_jwt(auth_token).user.id
        temp_credit, perm_credit = credits.get_credit(user_id)
        return CreditResponse(temp_credit=temp_credit, perm_credit=perm_credit)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))

# TODO deprecate
# @router.get("/temp/{user_id}", response_model=TempCreditResponse)
# def get_temp_credit(user_id: str) -> TempCreditResponse:
#     """
#     Get the temp credit from a specific user.

#      - param request: `user_id` type of string. The unique uuid of the user,\n
#      - return: `credit`, the temp credit of the user.\n
#     """
#     try:
#         temp_credit = credits.get_temp_credit(user_id)
#         return TempCreditResponse(credit=temp_credit)
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/perm/{user_id}", response_model=PermCreditResponse)
# def get_perm_credit(user_id: str) -> PermCreditResponse:
#     """
#     Get the perm credit from a specific user.

#      - param request: `user_id` type of string. The unique uuid of the user,\n
#      - return: `credit`, the perm credit of the user.\n
#     """
#     try:
#         perm_credit = credits.get_perm_credit(user_id)
#         return PermCreditResponse(credit=perm_credit)
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# TODO deprecate
# @router.post("/{user_id}", response_model=NewCreditResponse)
# def create_credit(user_id: str) -> NewCreditResponse:
#     """
#     Create a credit record for a given user in DB.

#     - param request: `user_id` type of string. The unique uuid of the user,\n
#     - return: `id` type of uuid. The credit record's unique id, \n
#     """
#     try:
#         credit_id = credits.create_credit(user_id)
#         return NewCreditResponse(id=credit_id)
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# @router.put("/temp", response_model=TempCreditResponse)
# def update_temp_credit(request: UpdateCreditRequest) -> TempCreditResponse:
#     """
#     Update the temp credit for a user.

#     - param request: `UpdateCreditRequest`, including two fields,\n
#       - `user_id`: The unique uuid of the user\n
#       - `credit`: The new credit value to be updated\n
#     - return: `credit`, the new temp credit amount\n
#     """
#     try:
#         response = credits.update_temp_credit(request)
#         return TempCreditResponse(credit=response.data[0]["temp_credit"])
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.put("/perm", response_model=PermCreditResponse)
# def update_perm_credit(request: UpdateCreditRequest) -> PermCreditResponse:
#     """
#     Update the perm credit for a user.

#     - param request: `UpdateCreditRequest`, including two fields,\n
#       - `user_id`: The unique uuid of the user\n
#       - `credit`: The new credit value to be updated\n
#     - return: `credit`, the new perm credit amount\n
#     """
#     try:
#         response = credits.update_perm_credit(request)
#         return PermCreditResponse(credit=response.data[0]["perm_credit"])
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.put("", response_model=DeleteCreditResponse)
# def decrement_credit(request: DecrementCreditRequest) -> DeleteCreditResponse:
#     """
#     Decrement a user's credit according to COST_PER_QUESTION constant.

#     - param request: `DecrementCreditRequest`, including one field,\n
#       - `user_id`: The unique uuid of the user\n
#     - return: `True`, Always returns true. \n
#       - Will throw error when user doesn't have enough credit\n
#     """
#     try:
#         credits.decrement_credit(request.user_id)
#         return DeleteCreditResponse(success=True)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=405,
#             detail=f"User: {request.user_id} doesn't have enough credits to create a new chat",
#         )
#     except Exception as e:
#         logging.error(e)
#         raise HTTPException(status_code=500, detail=str(e))
