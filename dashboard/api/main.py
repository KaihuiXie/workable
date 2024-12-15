import jwt
import logging
from flask import Flask, request, jsonify

from routers.users import users_bp
from routers.resume import resume_bp
from common.objects import SECRET_KEY

app = Flask(__name__)

app.register_blueprint(users_bp)
app.register_blueprint(resume_bp)

# List of endpoints that do not require authentication
# EXEMPT_ENDPOINTS = ['/healthcheck', '/users/login', '/users/register', '/users/logout', '/resume/upload']

# @app.before_request
# def require_token():
#     if request.path in EXEMPT_ENDPOINTS:
#         return
#     token = None
#     # Check for the token in the Authorization header
#     if 'Authorization' in request.headers:
#         token = request.headers['Authorization'].split(" ")[1]
#     if not token:
#         return jsonify({"detail": "Token is missing"}), 401

#     try:
#         jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#     except jwt.ExpiredSignatureError:
#         return jsonify({"detail": "Token has expired"}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({"detail": "Invalid token"}), 401

@app.route("/healthcheck", methods=["GET"])
def health_check():
    try:
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(f"Health Check Failed: {e}")
        return jsonify({"detail": "Service unavailable"}), 500
    
if __name__ == '__main__':
   app.run(port=8080)