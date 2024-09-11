import time
from fastapi import Request, HTTPException
# from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import JSONResponse
from common.objects import users

# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # List of paths that require authentication
#         if request.method == "OPTIONS":
#             response = await call_next(request)
#             return response
#         closed_paths = [
#             "/logout",
#             "/user_info",
#             "/reset_password",
#             "/update_password",
#             "/user_subscription",
#             "/user_subscription/info",
#             "/new_chat",
#             "/chat/",
#             "/shared_chat/create",
#             "/shared_chat/",
#             "/create_checkout_session",
#             "/credit",
#             "/url_platforms/update_user_profile"
#         ]
#         auth_header = request.headers.get("Authorization")
#         if any(request.url.path.startswith(path) for path in closed_paths):
#             if not auth_header:
#                 return JSONResponse({"error": "Unauthorized"}, status_code=401)

#             try:
#                 token = auth_header.replace("Bearer ", "")
#                 users.verify_jwt(token)
#             except HTTPException:
#                 return JSONResponse({"error": "Unauthorized"}, status_code=401)
            
#         response = await call_next(request)
#         return response
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
