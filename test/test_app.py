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


# def test_get_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.get(f"/credit/{user_id}")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200

# def test_get_temp_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.get(f"/credit/temp/{user_id}")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200
#
#
# def test_get_perm_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.get(f"/credit/perm/{user_id}")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_decrement_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#
#     payload = {
#         "user_id": user_id,
#     }
#
#     response = client.put("/credit", json=payload)
#     print(response.json)
#     logging.error(response.json())
#     assert response.status_code == 200

# With an exist, and not expired token.
# Will return true, and the referrer_id
# def test_get_referrer_success_case():
#     invitation_token = "c99770af-f316-4377-ad28-a65c032e03ee"
#
#     response = client.get(f"/referrer/{invitation_token}")
#     logging.error(response.json())
#     print(response.json())
#     assert response.status_code == 200


# With a random token that does not exist
# will return false, and an empty referrer_id
# def test_get_referrer_wrong_token_case():
#     invitation_token = "3d9e633f-542b-47ab-9606"
#
#     response = client.get(f"/referrer/{invitation_token}")
#     logging.error(response.json())
#     print(response.json())
#     assert response.status_code == 200


# need to use a expired token
# will return false, and a referrer id.
# So that front end can create an alert for user to ask for referrer to refresh token
# def test_get_referrer_expire_case():
#     invitation_token = "36993590-7a33-4fc6-944f-1ad0a6b63782"
#
#     response = client.get(f"/referrer/{invitation_token}")
#     logging.error(response.json())
#     print(response.json())
#     assert response.status_code == 200


# for create a new token case: need to use a new user_id that doesn't have a invitation token
# for getting existing token case: need to use a user_id that have a not expired token
# for expired case: need to use a user_id that has an expired token
# def test_get_invitation_success_case():
#     user_id = "a4804bea-93d8-4789-969d-19b5364f7436"
#     response = client.get(f"/invitation/{user_id}")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_credit():
#     user_id = "450f6a7f-8f91-406b-b130-571abbdcef4d"
#     response = client.get(f"/credit/{user_id}")
#     print(response.json())
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
#     image_file_path = "./limit.jpeg"
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
#     response = client.post("/question", data=payload)
#     print(response.json())  # Log the JSON response
#     assert response.status_code == 200


# def test_examples():
#     response = client.get("/examples")
#     logging.error(response.json())
#     print(response.json())  # Log the JSON response
#     assert response.status_code == 200


# def test_all_chats():
#     payload = {
#         "user_id": "a4804bea-93d8-4789-969d-19b5364f7436",
#     }
#     response = client.post("/all_chats", json=payload)
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_helper():
#     payload = {
#         "chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70",
#     }
#     response = client.post("/solve", json=payload)
#     assert response.status_code == 200

# def test_helper_cn():
#     payload = {
#         "chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70",
#         "language": "ZH"
#     }
#     response = client.post("/solve", json=payload)
#     assert response.status_code == 200


# def test_learner():
#     payload = {
#         "chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70",
#     }
#     response = client.post("/solve", json=payload)
#     assert response.status_code == 200


# def test_chat():
#     payload = {"chat_id": "0786ddb2-001d-4635-9bd0-25ff23893f70", "query": "what's new"}
#     response = client.post("/chat", json=payload)
#     assert response.status_code == 200


# def test_get_chat():
#     chat_id = "f1d30395-91c4-4e0a-8753-43ee99fa9b4f"
#     response = client.get(f"/chat/{chat_id}")
#     print(response.json())
#     assert response.status_code == 200


# def __login(request):
#     response = client.post(f"/login", json=request)
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200
#
#
# def test_login():
#     request = {
#         "email": "bowen.shawn.xiao@gmail.com",
#         "phone": None,
#         "password": "Shengdian123",
#     }
#     __login(request)
#     request = {
#         "email": "bowen.shawn.xiao@gmail.com",
#         "password": "Shengdian123",
#     }
#     __login(request)
#     request = {
#         "email": "bowen.shawn.xiao@gmail.com",
#         "phone": "1234567890",
#         "password": "Shengdian123",
#     }
#     __login(request)
#
#
# def test_logout():
#     request = {
#         "email": "bowen.shawn.xiao@gmail.com",
#         "password": "Shengdian123",
#     }
#     client.post(f"/login", json=request)
#     response = client.post("/logout")
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200


# def test_signup():
#     request = {
#         "email": "test19@xxmail.com",
#         "phone": None,
#         "password": "test123",
#     }
#     response = client.post(f"/signup", json=request)
#     print(response.json())
#     logging.error(response.json())
#     assert response.status_code == 200
