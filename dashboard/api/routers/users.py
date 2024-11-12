import logging
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import Unauthorized, InternalServerError
from pydantic import ValidationError
from flask_pydantic import validate

from common.objects import users
from src.users.interfaces import (
    SignInRequest,
    SignUpRequest,
)

# BluePrint setup.
users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/login', methods=['POST'])
@validate()
def login(body: SignInRequest):
    try:
        res = users.login_user(body.email, body.password)
        return res
    except Exception as e:
        logging.error(f"Server error: {e}")
        return jsonify({"detail": "Service unavailable"}), 500

@users_bp.route('/register', methods=['POST'])
@validate()
def register(body: SignUpRequest):
    try:
        res = users.register_user(body.email, body.password, body.name)
        if res:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"detail": "Service unavailable"}), 500
    except Exception as e:
        logging.error(f"Server error: {e}")
        return jsonify({"detail": "Service unavailable"}), 500
       
@users_bp.route("/user/login", methods=["POST"])
def user_login():
    data = request.get_json()
    userName = data.get("userName")
    password = data.get("password")
    if userName == "admin" and password == "123456":
        return jsonify({
            "code": 0,
            "data": {
                "token": "666666"
            }
        })
    else:
        return jsonify({
            "code": 99999999,
            "msg": "err msg"
        })


@users_bp.route("/user/info", methods=["GET", "POST"])
def user_info():
    token = request.headers.get("token")
    if token == "666666":
        return jsonify({
            "code": 0,
            "data": {
                "id": "1",
                "userName": "admin",
                "realName": "xue",
                "userType": 1
            }
        })
    return jsonify({
        "code": 99990403,
        "msg": "token err"
    })
