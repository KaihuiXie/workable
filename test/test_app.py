import base64
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from PIL import Image
import logging
import os

from src.interfaces import SignInRequest

# Configure logging at the top of your test file
logging.basicConfig(level=logging.INFO)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.main import app

client = TestClient(app)


def test_examples():
    response = client.get("/examples")
    logging.error(response.json())
    print(response.json())  # Log the JSON response
    assert response.status_code == 200


def test_all_chats():
    payload = {
        "user_id": "a4804bea-93d8-4789-969d-19b5364f7436",
    }
    response = client.post("/all_chats", json=payload)
    print(response.json())
    logging.error(response.json())
    assert response.status_code == 200


def test_helper():
    payload = {
        "chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70",
    }
    response = client.post("/solve", json=payload)
    assert response.status_code == 200


def test_helper_cn():
    payload = {"chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70", "language": "ZH"}
    response = client.post("/solve", json=payload)
    assert response.status_code == 200


def test_learner():
    payload = {
        "chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70",
    }
    response = client.post("/solve", json=payload)
    assert response.status_code == 200


def test_chat():
    payload = {"chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70", "query": "what's new"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200


def test_get_chat():
    chat_id = "d4531219-bbd3-4613-8142-01cb0c50a29d"
    response = client.get(f"/chat/{chat_id}")
    print(response.json())
    assert response.status_code == 200


def __login(request):
    response = client.post(f"/login", json=request)
    print(response.json())
    logging.error(response.json())
    assert response.status_code == 200


def test_login():
    request = {
        "email": "bowen.shawn.xiao@gmail.com",
        "phone": None,
        "password": "Shengdian123",
    }
    __login(request)
    request = {
        "email": "bowen.shawn.xiao@gmail.com",
        "password": "Shengdian123",
    }
    __login(request)
    request = {
        "email": "bowen.shawn.xiao@gmail.com",
        "phone": "1234567890",
        "password": "Shengdian123",
    }
    __login(request)


def test_logout():
    request = {
        "email": "bowen.shawn.xiao@gmail.com",
        "password": "Shengdian123",
    }
    client.post(f"/login", json=request)
    response = client.post("/logout")
    print(response.json())
    logging.error(response.json())
    assert response.status_code == 200


def test_oauth_login():
    request = {
        "provider": "google",
    }
    response = client.post(f"/login/oauth", json=request)
    print(response.json())
    logging.error(response.json())
    assert response.status_code == 200


def test_signup():
    request = {
        "email": "test19@xxmail.com",
        "phone": None,
        "password": "test123",
    }
    response = client.post(f"/signup", json=request)
    print(response.json())
    logging.error(response.json())
    assert response.status_code == 200


def test_get_session():
    request = {
        "email": "bowen.shawn.xiao@gmail.com",
        "phone": None,
        "password": "Shengdian123",
    }
    __login(request)

    response = client.get(f"/session")
    print(response.json())
    logging.error(response.json())
    assert response.status_code == 200
