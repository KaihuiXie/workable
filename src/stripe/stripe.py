import stripe
from fastapi import HTTPException
from src.supabase.async_supabase import AsyncSupabase
from src.email.sendgrid import EmailService
import datetime

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

    def get_customer_info(self, email):
        try:
            customers = stripe.Customer.list(email=email).data
            if not customers:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            customer = customers[0]  
            payment_methods = stripe.PaymentMethod.list(customer=customer.id, type="card")
            if not payment_methods.data:
                raise HTTPException(status_code=404, detail="No payment methods found")

            card_last4 = payment_methods.data[0].card.last4
            card_exp_month = payment_methods.data[0].card.exp_month
            card_exp_year = payment_methods.data[0].card.exp_year

            subscriptions = stripe.Subscription.list(customer=customer.id, status="active").data

            if not subscriptions:
                raise HTTPException(status_code=404, detail="No active subscriptions found")
            
            plan_name = subscriptions[0].plan.nickname
            product_id = subscriptions[0].plan.product

            product = stripe.Product.retrieve(product_id)
            product_name = product.name
            next_payment_date = datetime.datetime.fromtimestamp(subscriptions[0].current_period_end)

            return {
                "email": email,
                "card_last4": card_last4,
                "card_expiry": f"{card_exp_month}/{card_exp_year}",
                "subscription_plan": product_name,
                "next_payment_date": next_payment_date.strftime("%Y-%m-%d %H:%M:%S")
            }

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))