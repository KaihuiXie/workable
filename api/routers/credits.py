import logging

from fastapi import HTTPException, APIRouter
from common.object import supabase
from src.interfaces import DecrementCreditRequest, UpdateCreditRequest

router = APIRouter(
    # prefix="/credits",
    tags=["credits"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/credit/{user_id}")
async def create_credit(user_id: str):
    try:
        id = supabase.create_credit(user_id)
        return {"id": id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/{user_id}")
async def get_credit(user_id: str):
    try:
        temp_credit = supabase.get_temp_credit_by_user_id(user_id)
        perm_credit = supabase.get_perm_credit_by_user_id(user_id)
        return {"temp_credit": temp_credit, "perm_credit": perm_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/temp/{user_id}")
async def get_temp_credit(user_id: str):
    try:
        response = supabase.get_temp_credit_by_user_id(user_id)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/perm/{user_id}")
async def get_perm_credit(user_id: str):
    try:
        response = supabase.get_perm_credit_by_user_id(user_id)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit/temp")
async def update_temp_credit(request: UpdateCreditRequest):
    try:
        response = supabase.update_temp_credit_by_user_id(
            request.user_id, request.credit
        )
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit/perm")
async def update_perm_credit(request: UpdateCreditRequest):
    try:
        response = supabase.update_perm_credit_by_user_id(
            request.user_id, request.credit
        )
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit")
async def decrement_credit(request: DecrementCreditRequest):
    try:
        supabase.decrement_credit(request.user_id)
        return {"decremental": True}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
