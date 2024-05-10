import logging

from fastapi import APIRouter, HTTPException

from common.objects import credits
from src.credits.interfaces import DecrementCreditRequest, UpdateCreditRequest

router = APIRouter(
    # prefix="/credits",
    tags=["credits"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/credit/{user_id}")
async def create_credit(user_id: str):
    try:
        id = credits.create_credit(user_id)
        return {"id": id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/{user_id}")
async def get_credit(user_id: str):
    try:
        temp_credit, perm_credit = credits.get_credit(user_id)
        return {"temp_credit": temp_credit, "perm_credit": perm_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/temp/{user_id}")
async def get_temp_credit(user_id: str):
    try:
        temp_credit = credits.get_temp_credit(user_id)
        return {"credit": temp_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credit/perm/{user_id}")
async def get_perm_credit(user_id: str):
    try:
        perm_credit = credits.get_perm_credit(user_id)
        return {"credit": perm_credit}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit/temp")
async def update_temp_credit(request: UpdateCreditRequest):
    try:
        response = credits.update_temp_credit(request)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit/perm")
async def update_perm_credit(request: UpdateCreditRequest):
    try:
        response = credits.update_perm_credit(request)
        return {"credit": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit")
async def decrement_credit(request: DecrementCreditRequest):
    try:
        credits.decrement_credit(request)
        return {"decremental": True}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
