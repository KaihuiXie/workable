import stripe
from fastapi import HTTPException
from src.supabase.async_supabase import AsyncSupabase
from src.email.sendgrid import EmailService
class Stripe:
    def __init__(self, apikeys, endpoint_key, supabase_url, supabase_key, ems:EmailService):
        stripe.api_key = apikeys
        self.endpoint_key = endpoint_key
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.ems = ems

    async def process_event(self, payload, sig_header):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.endpoint_key
            )
                # Process the event
            if event["type"] == "customer.subscription.created":
                subscription = event["data"]["object"]
                customer_id = subscription['customer']
                # Retrieve the customer object
                customer = stripe.Customer.retrieve(customer_id)
                # Get the customer's email
                customer_email = customer.get('email')
                await self.update_premium(customer_email, True)
                # Handle successful payment here
                await self.ems.send_subscription_email(customer_email)

            elif event["type"] == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                print(f"Subscription canceled: {subscription['id']}")
                customer_id = subscription['customer']
                # Retrieve the customer object
                customer = stripe.Customer.retrieve(customer_id)
                # Get the customer's email
                customer_email = customer.get('email')
                await self.update_premium(customer_email, False)
                # Handle subscription cancellation here
                # You can notify the user, update the database, etc.
                await self.ems.send_unsubscription_email(customer_email)

        except ValueError as e:
            # Invalid payload
            print(e)
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(e)
            raise HTTPException(status_code=400, detail="Invalid signature")
        
    async def update_premium(self, email, status):
        supabase = await AsyncSupabase.create(self.supabase_url, self.supabase_key)
        await supabase.update_premium(email, status)
