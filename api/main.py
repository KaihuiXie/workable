import logging
import os

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.routers import chats, credits, invitations, shared_chats, url_platforms, users
from common.objects import supabase
from src.middlewares import ExtendTimeoutMiddleware, TimerMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)

tags_metadata = [
    {
        "name": "users",
        "description": "TODO",  # TODO: add description
    },
    {
        "name": "chats",
        "description": "TODO",  # TODO: add description
    },
    {
        "name": "shared_chat",
        "description": "Operations with sharing chat.",
    },
    {
        "name": "credits",
        "description": "TODO",  # TODO: add description
    },
    {
        "name": "invitations",
        "description": "TODO",  # TODO: add description
    },
    {
        "name": "url_platforms",
        "description": "Tracking user source platform",
    },
]

# FastAPI
app = FastAPI(openapi_tags=tags_metadata)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://react-learning-app-blush.vercel.app",
        "http://react-learning-app-blush.vercel.app",
        "https://react-learning-app-be-main.vercel.app",
        "https://react-learning-app-rnpg.vercel.app",
        "https://bedev.mathsolver.top",
        "https://fedev.mathsolver.top",
        "http://localhost:3000",
        "https://localhost:3000",
        "https://chat.mathsolver.top",
        "http://chat.mathsolver.top",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(ExtendTimeoutMiddleware)
app.add_middleware(TimerMiddleware)
app.include_router(shared_chats.router)
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(invitations.router)
app.include_router(credits.router)
app.include_router(url_platforms.router)


@app.get("/health")
async def health_check():
    try:
        return {"status": "up"}
    except Exception as e:
        logging.error(f"Health Check Failed: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable")


@app.get("/examples")
async def get_examples():
    try:
        current_directory = os.path.dirname(os.path.realpath(__file__))
        with open(f"{current_directory}/config/example_chat_ids.yaml", "r") as file:
            example_chat_ids = yaml.safe_load(file)["chat_ids"]
            response = supabase.get_chats_by_ids(example_chat_ids)
            return {"data": response}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
