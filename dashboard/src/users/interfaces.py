from typing import Optional
from marshmallow import Schema, fields

# Define Marshmallow schema
class SignInRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    name = fields.Str(required=False, allow_none=True)

class UserInfoSchema(Schema):
    user_id = fields.Int(required=True)
    email = fields.Str(required=True)
    name = fields.Str(required=False, allow_none=True)
    token = fields.Str(required=True)

    