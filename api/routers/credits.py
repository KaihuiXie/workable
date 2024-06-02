import logging

from fastapi import APIRouter, HTTPException

from common.objects import credits
from src.credits.interfaces import DecrementCreditRequest, UpdateCreditRequest

router = APIRouter(
    tags=["credits"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/credit/{user_id}")
async def create_credit(user_id: str):
    """
    Create a credit record for a given user in DB.

    - param request: `user_id` type of string. The unique uuid of the user,\n
    - return: `id` type of uuid. The credit record's unique id, \n
    """
    try:
        id = credits.create_credit(user_id)
        return {"id": id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/{user_id}")
async def get_credit(user_id: str):
    """
    Get the temp and perm credits from a specific user.

    - param request: `user_id` type of string. The unique uuid of the user,\n
    - return: `temp_credit` and `perm_credit` in an array with index 0 is temp_credit, 1 is perm_credit.\n
    """
    try:
        temp_credit, perm_credit = credits.get_credit(user_id)
        return {"temp_credit": temp_credit, "perm_credit": perm_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/temp/{user_id}")
async def get_temp_credit(user_id: str):
    """
   Get the temp credit from a specific user.

    - param request: `user_id` type of string. The unique uuid of the user,\n
    - return: `credit`, the temp credit of the user.\n
    """
    try:
        temp_credit = credits.get_temp_credit(user_id)
        return {"credit": temp_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/perm/{user_id}")
async def get_perm_credit(user_id: str):
    """
   Get the perm credit from a specific user.

    - param request: `user_id` type of string. The unique uuid of the user,\n
    - return: `credit`, the perm credit of the user.\n
    """
    try:
        perm_credit = credits.get_perm_credit(user_id)
        return {"credit": perm_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit/temp")
async def update_temp_credit(request: UpdateCreditRequest):
    """
    Update the temp credit for a user.

    - param request: `UpdateCreditRequest`, including two fields,\n
      - `user_id`: The unique uuid of the user\n
      - `credit`: The new credit value to be updated\n
    - return: `credit`, the new temp credit amount\n
    """
    try:
        response = credits.update_temp_credit(request)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit/perm")
async def update_perm_credit(request: UpdateCreditRequest):
    """
    Update the perm credit for a user.

    - param request: `UpdateCreditRequest`, including two fields,\n
      - `user_id`: The unique uuid of the user\n
      - `credit`: The new credit value to be updated\n
    - return: `credit`, the new perm credit amount\n
    """
    try:
        response = credits.update_perm_credit(request)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit")
async def decrement_credit(request: DecrementCreditRequest):
    """
    Decrement a user's credit according to COST_PER_QUESTION constant.

    - param request: `DecrementCreditRequest`, including one field,\n
      - `user_id`: The unique uuid of the user\n
    - return: `True`, Always returns true. \n
      - Will throw error when user doesn't have enough credit\n
    """
    try:
        credits.decrement_credit(request)
        return {"decremental": True}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
