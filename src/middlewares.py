import time
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from common.objects import users

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # List of paths that require authentication
        closed_paths = [
            "/logout",
            "/user_info",
            "/reset_password",
            "/update_password",
            "/user_subscription",
            "/user_subscription/info",
            "/new_chat",
            "/chat/",
            "/shared_chat/create",
            "/shared_chat/",
            "/create_checkout_session",
            "/credit",
            "/url_platforms/update_user_profile"
        ]

        if any(request.url.path.startswith(path) for path in closed_paths):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return RedirectResponse(url="/login", status_code=307)

            try:
                token = auth_header.replace("Bearer ", "")
                users.verify_jwt(token)
            except Exception:
                return RedirectResponse(url="/login", status_code=307)

        response = await call_next(request)
        return response
class ExtendTimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["timeout"] = "100"  # Extend timeout to 100 seconds
        return response

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
