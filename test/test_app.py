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


# def test_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.get(f"/credit/{user_id}")
#     logging.error(response.json())
#     assert response.status_code == 200


# This test would fail for 2 reasons:
# 1. credit record has been created. To pass: delete the old record in Supabase
# 2. user_id doesn't exist in auth.users. To pass: need to use a existing user_id
# def test_create_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.post(f"/credit/{user_id}")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_get_first_sign_in():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.get(f"/first_sign_in_of_the_day/{user_id}")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200

# def test_update_temp_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     credit_amount = 12
#
#     payload = {
#         "user_id": user_id,
#         "credit": credit_amount,
#     }
#
#     response = client.put("/credit/temp", json=payload)
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_update_perm_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     credit_amount = 12
#
#     payload = {
#         "user_id": user_id,
#         "credit": credit_amount,
#     }
#
#     response = client.put("/credit/perm", json=payload)
#     logging.error(response.json())
#     assert response.status_code == 200

# def test_image():
#     image_file_path = "./iphone.HEIC"
#     # image_file_path = "./phone.jpeg"
#     try:
#         with open(image_file_path, "rb") as image_file:
#             data = {
#                 "user_id": "6e0d1fed-8845-488e-832d-4c767f0f5bb0",
#                 "mode": "learner",
#                 # "prompt": "Optional prompt here if needed",
#             }
#             files = {
#                 "image_file": image_file,
#             }
#             response = client.post("/question", data=data, files=files)
#             print(response.json())
#             assert response.status_code == 200
#     except Exception as e:
#         logging.error(e)

# def test_image_with_prompt():
#     image_file_path = "./2024.png"
#     with open(image_file_path, "rb") as image_file:
#         data = {
#             "user_id": "6e0d1fed-8845-488e-832d-4c767f0f5bb0",
#             "mode": "helper",
#             "prompt": "Solve this",
#         }
#         files = {
#             "image_file": image_file,
#         }
#         response = client.post("/question", data=data, files=files)
#         print(response.json())
#         assert response.status_code == 200


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
