import base64
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from PIL import Image
import logging
import os

# Configure logging at the top of your test file
logging.basicConfig(level=logging.info)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.main import app

client = TestClient(app)

# def test_image():
#     image_file_path = "./simple.png"
#     with open(image_file_path, "rb") as image_file:
#         # Read the file's content
#         binary_data = image_file.read()
#         # Encode the binary data to a base64 string
#         base64_encoded_string = base64.b64encode(binary_data).decode("utf-8")

#     payload = {
#         "user_id": "ed6f1826-5c5c-4cae-a45a-3dd5cabb2076",
#         "image_string": base64_encoded_string,
#     }
#     response = client.post("/image/", json=payload)
#     logging.debug(response.json())  # Log the JSON response
#     assert response.status_code == 200


# def test_all_chats():
#     payload = {
#         "user_id": "ed6f1826-5c5c-4cae-a45a-3dd5cabb2076",
#     }
#     response = client.post("/all-chats/", json=payload)
#     logging.error(response.json())
#     assert response.status_code == 200

# def test_helper():
#     payload = {
#         "chat_id": "b3833758-6f24-4695-a076-9d82c2e5c0e1",
#     }
#     response = client.post("/helper/", json=payload)
#     assert response.status_code == 200

# def test_learner():
#     payload = {
#         "chat_id": "b3833758-6f24-4695-a076-9d82c2e5c0e1",
#     }
#     response = client.post("/learner/", json=payload)
#     assert response.status_code == 200


def test_chat():
    payload = {"chat_id": "b3833758-6f24-4695-a076-9d82c2e5c0e1", "query": "what's new"}
    response = client.post("/chat/", json=payload)
    assert response.status_code == 200
