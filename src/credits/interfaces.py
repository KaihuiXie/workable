from pydantic import BaseModel


class UpdateCreditRequest(BaseModel):
    user_id: str
    credit: int


class DecrementCreditRequest(BaseModel):
    user_id: str
