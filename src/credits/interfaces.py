from pydantic import BaseModel, Field


class UpdateCreditRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user")
    credit: int = Field(..., description="The credit to update")


class DecrementCreditRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user")


class NewCreditResponse(BaseModel):
    id: str = Field(..., description="The ID of the credit record")


class CreditResponse(BaseModel):
    temp_credit: int = Field(..., description="The temp credit of the user")
    perm_credit: int = Field(..., description="The perm credit of the user")


class TempCreditResponse(BaseModel):
    credit: int = Field(..., description="The temp credit of the user")


class PermCreditResponse(BaseModel):
    credit: int = Field(..., description="The perm credit of the user")


class DeleteCreditResponse(BaseModel):
    success: bool = Field(..., description="Whether the deletion was successful")
