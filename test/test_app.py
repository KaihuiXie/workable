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
#         "user_id": "6e0d1fed-8845-488e-832d-4c767f0f5bb0",
#         "image_string": base64_encoded_string,
#         "mode": "learner",
#     }
#     response = client.post("/question", json=payload)
#     logging.debug(response.json())  # Log the JSON response
#     assert response.status_code == 200


# def test_no_image():

#     payload = {
#         "user_id": "6e0d1fed-8845-488e-832d-4c767f0f5bb0",
#         "prompt": "There are chicken and rabbits in the cage. They are in total 10 heads and 20 feet. How many rabbits? ",
#         "mode": "learner",
#     }
#     response = client.post("/question", json=payload)
#     print(response.json())  # Log the JSON response
#     assert response.status_code == 200

# def test_examples():
#     response = client.get("/examples")
#     logging.error(response.json())
#     print(response.json())  # Log the JSON response
#     assert response.status_code == 200


# def test_all_chats():
#     payload = {
#         "user_id": "6e0d1fed-8845-488e-832d-4c767f0f5bb0",
#     }
#     response = client.post("/all_chats", json=payload)
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_helper():
#     payload = {
#         "chat_id": "e4aa146f-86d7-4cd1-a687-bc4acbaa921f",
#     }
#     response = client.post("/solve", json=payload)
#     assert response.status_code == 200


# def test_learner():
#     payload = {
#         "chat_id": "2121490b-a396-45fd-aaa4-4abf785443e7",
#     }
#     response = client.post("/solve", json=payload)
#     assert response.status_code == 200


# def test_chat():
#     payload = {"chat_id": "2121490b-a396-45fd-aaa4-4abf785443e7", "query": "what's new"}
#     response = client.post("/chat", json=payload)
#     assert response.status_code == 200

# def test_get_chat():
#     chat_id = "f1d30395-91c4-4e0a-8753-43ee99fa9b4f"
#     response = client.get(f"/chat/{chat_id}")
#     print(response.json())
#     assert response.status_code == 200
