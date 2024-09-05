from pydantic import BaseModel

class CheckoutSessionRequest(BaseModel):
    email: str
    priceId: str
    successUrl: str
    cancelUrl: str