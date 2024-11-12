import logging
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from common.objects import SECRET_KEY
from common.objects import users
from src.users.interfaces import (
    SignInRequestSchema,
    UserInfoSchema,
)

# BluePrint setup.
users_bp = Blueprint('users', __name__, url_prefix='/users')
    
@users_bp.route('/login', methods=['POST'])
def login():
    schema = SignInRequestSchema()
    try:
        body = schema.load(request.get_json())
        response = users.login_user(body['email'])
        password = body['password']
        if response and bcrypt.checkpw(password.encode('utf-8'), response['password'].encode('utf-8')):
            user_id = response['id']
            user_email = response['email']
            user_name = response['username']
            # JWT token expires in 1 hour
            payload = {
                'user_id': user_id,
                'email': user_email,
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            user_info = UserInfoSchema().dump({
                'user_id': user_id,
                'email': user_email,
                'name': user_name,
                'token': token
            })
            return jsonify(user_info), 200
        else:
            return jsonify({'detail': 'Invalid email or password'}), 401
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        logging.error(f'Server error: {e}')
        return jsonify({'detail': 'Service unavailable'}), 500

@users_bp.route('/register', methods=['POST'])
def register():
    schema = SignInRequestSchema()
    try:
        body = schema.load(request.get_json())
        password = body['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')
        res = users.register_user(body['email'], hashed_password_str, body['name'])
        if res:
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'detail': 'Service unavailable'}), 500
    except Exception as e:
        logging.error(f'Server error: {e}')
        return jsonify({'detail': 'Service unavailable'}), 500

@users_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # For JWT, logging out is simply removing the token on the client side.
        return jsonify({'status': 'ok', 'detail': 'Successfully logged out'}), 200
    except Exception as e:
        logging.error(f'Server error: {e}')
        return jsonify({'detail': 'Service unavailable'}), 500
