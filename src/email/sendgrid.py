import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import HTTPException, status
import smtplib
import dns.resolver
import re

class EmailService:
    def __init__(self, api,email_header):
        self.client = SendGridAPIClient(api)
        self.from_email = email_header

    def send_invitation_email(self, email, redirect_url):
        try:
            html_content=f"""
            <p>You have been invited to create a user on MathSolver! 
            Follow this link to accept the invite:</p>
            <p><a href="{redirect_url}" style="font-size: 16px; color: #007bff; text-decoration: none;">
            Accept the invite</a></p>
            """
            message = Mail(
                from_email = self.from_email,
                to_emails = email,
                subject = "You have been invited",
                html_content=html_content
            )
            response = self.client.send(message)
            return response
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    def is_valid_email_format(self, email):
        try:
            regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            return re.match(regex, email) is not None
        except:
            return False
    def is_valid_domain(self, email):
        try:
            domain = email.split('@')[1]
            dns.resolver.resolve(domain, 'MX')
            return True
        except:
            return False

    def verify_email(self, email):
        return self.is_valid_domain(email) and self.is_valid_email_format(email)