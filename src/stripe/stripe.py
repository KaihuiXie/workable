import stripe
from fastapi import HTTPException

class Stripe:
    def __init__(self, apikeys, endpoint_key):
        self.apikeys = apikeys
        self.endpoint_key = endpoint_key

    def construct_event(self, payload, sig_header):
        try:
            print(self.endpoint_key)
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.endpoint_key
            )
            return event
        except ValueError as e:
            # Invalid payload
            print(e)
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(e)
            raise HTTPException(status_code=400, detail="Invalid signature")