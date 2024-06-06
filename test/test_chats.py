import json
import logging
import os
import sys
import unittest
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from common.constants import EVERY_DAY_CREDIT_INCREMENT, ROOT_DIR
from common.objects import credits
from src.chats.supabase import ChatsSupabase
from src.credits.interfaces import UpdateCreditRequest
from src.math_agent.math_agent import MathAgent
from src.supabase.supabase import Supabase


class ChatsTest(unittest.TestCase):
    # TEST_USER_ID
    user_id = "6e0d1fed-8845-488e-832d-4c767f0f5bb0"
    image_path = ROOT_DIR + "/test/resources/limit.jpeg"
    supabase = None
    math_agent = None

    @classmethod
    def setUpClass(cls):
        logging.disable(level=logging.ERROR)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        cls.test_client = TestClient(app)
        cls.__init_supabase()
        cls.__init_math_agent()

    @classmethod
    def tearDownClass(cls):
        ...

    @classmethod
    def __init_supabase(cls):
        load_dotenv()
        cls.supabase = ChatsSupabase(
            Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        )

    @classmethod
    def __init_math_agent(cls):
        load_dotenv()
        cls.math_agent = MathAgent(
            os.getenv("OPENAI_API_KEYS"),
            os.getenv("WOLFRAM_ALPHA_APP_ID"),
            cls.supabase,
        )

    def setUp(self):
        # make sure test user has enough credits
        credits.update_temp_credit(
            UpdateCreditRequest(user_id=self.user_id, credit=EVERY_DAY_CREDIT_INCREMENT)
        )
        credits.update_perm_credit(
            UpdateCreditRequest(user_id=self.user_id, credit=EVERY_DAY_CREDIT_INCREMENT)
        )

    def tearDown(self):
        credits.update_temp_credit(
            UpdateCreditRequest(user_id=self.user_id, credit=EVERY_DAY_CREDIT_INCREMENT)
        )
        credits.update_perm_credit(
            UpdateCreditRequest(user_id=self.user_id, credit=EVERY_DAY_CREDIT_INCREMENT)
        )

    def __create_chat(self, question=None):
        chat_id = self.supabase.create_empty_chat(self.user_id)
        if question:
            self.supabase.update_question(chat_id, question=question)
        return chat_id

    def __delete_chat(self, chat_id):
        self.supabase.delete_chat_by_id(chat_id)

    # def test_new_chat_id(self):
    #     data = {
    #         "user_id": self.user_id,
    #     }
    #     response = self.test_client.post("/new_chat_id", json=data)
    #     self.assertEqual(response.status_code, 200)
    #     response_json = json.load(response)
    #     chat_id = response_json["chat_id"]
    #     self.__delete_chat(chat_id)

    #     # failure case
    #     credits.update_temp_credit(UpdateCreditRequest(user_id=self.user_id, credit=0))
    #     credits.update_perm_credit(UpdateCreditRequest(user_id=self.user_id, credit=0))
    #     response = self.test_client.post("/new_chat_id", json=data)
    #     self.assertEqual(response.status_code, 405)

    # def test_question_photo_learner_no_photo(self):
    #     data = {
    #         "user_id": self.user_id,
    #     }
    #     response = self.test_client.post("/new_chat_id", json=data)
    #     self.assertEqual(response.status_code, 200)
    #     response_json = json.load(response)
    #     chat_id = response_json["chat_id"]
    #     data = {"chat_id": chat_id, "mode": "learner", "prompt": "1+1=?"}
    #     response = self.test_client.post("/question_photo", data=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.__delete_chat(chat_id)

    def test_get_chat(self):
        chat_id = self.__create_chat()
        response = self.test_client.get(f"/chat/{chat_id}?user_id={self.user_id}")
        self.assertEqual(response.status_code, 200)
        response_json = json.load(response)
        self.assertEqual(response_json["payload"], None)
        self.assertEqual(response_json["question"], None)
        self.assertEqual(response_json["image_str"], None)
        self.assertEqual(response_json["chat_again"], True)
        self.__delete_chat(chat_id)

    def test_get_chat_no_access(self):
        test_user_id = "2913bd5a-91ed-43ff-ab49-f1e1f60c9ebc"  # qi.adsads@gmail.com
        no_access_chat_id = self.supabase.create_empty_chat(test_user_id)
        response = self.test_client.get(
            f"/chat/{no_access_chat_id}?user_id={self.user_id}"
        )
        self.assertEqual(response.status_code, 405)
        self.__delete_chat(no_access_chat_id)

    def test_get_chat_false_chat_again(self):
        chat_id = self.__create_chat()
        payload = {"messages": " " * 20}
        self.supabase.update_payload(chat_id, payload=payload)
        response = self.test_client.get(f"/chat/{chat_id}?user_id={self.user_id}")
        self.assertEqual(response.status_code, 200)
        response_json = json.load(response)
        self.assertEqual(response_json["payload"], payload)
        self.assertEqual(response_json["question"], None)
        self.assertEqual(response_json["image_str"], None)
        self.assertEqual(response_json["chat_again"], False)
        self.__delete_chat(chat_id)

    #     def test_all_chats(self):
    #         question = "1+1"
    #         chat_id_1 = self.__create_chat(question=question)
    #         chat_id_2 = self.__create_chat(question=question)

    #         response = self.test_client.get(f"/all_chats/{self.user_id}")
    #         self.assertEqual(response.status_code, 200)
    #         response_json = json.load(response)
    #         ids = [item["id"] for item in response_json["data"]]
    #         self.assertEqual(set(ids), set({chat_id_1, chat_id_2}))
    #         self.__delete_chat(chat_id_1)
    #         self.__delete_chat(chat_id_2)

    #     def test_question_photo_learner_no_prompt(self):
    #         chat_id = self.__create_chat()

    #         image_file_path = self.image_path
    #         with open(image_file_path, "rb") as image_file:
    #             data = {
    #                 "chat_id": chat_id,
    #                 "mode": "learner",
    #             }
    #             files = {
    #                 "image_file": image_file,
    #             }
    #             response = self.test_client.post("/question_photo", data=data, files=files)
    #             self.assertEqual(response.status_code, 200)
    #         self.__delete_chat(chat_id)

    #     def test_question_photo_helper_no_prompt(self):
    #         chat_id = self.__create_chat()

    #         image_file_path = self.image_path
    #         with open(image_file_path, "rb") as image_file:
    #             data = {
    #                 "chat_id": chat_id,
    #                 "mode": "helper",
    #             }
    #             files = {
    #                 "image_file": image_file,
    #             }
    #             response = self.test_client.post("/question_photo", data=data, files=files)
    #             self.assertEqual(response.status_code, 200)
    #         self.__delete_chat(chat_id)

    # def test_question_photo_learner_prompt(self):
    #     chat_id = self.__create_chat()

    #     image_file_path = self.image_path
    #     with open(image_file_path, "rb") as image_file:
    #         data = {
    #             "chat_id": chat_id,
    #             "mode": "learner",
    #             "prompt": "reply in Chinese",
    #         }
    #         files = {
    #             "image_file": image_file,
    #         }
    #         response = self.test_client.post("/question_photo", data=data, files=files)
    #         self.assertEqual(response.status_code, 200)
    #     payload = {
    #         "chat_id": chat_id,
    #     }
    #     response = self.test_client.post("/solve", json=payload)
    #     self.assertEqual(response.status_code, 200)
    #     self.__delete_chat(chat_id)

    def test_GRE_math_question_photo_helper_prompt(self):
        chat_id = self.__create_chat()

        image_file_path = self.image_path
        # image_file_path = ROOT_DIR + "/test/resources/GREMath.png"
        with open(image_file_path, "rb") as image_file:
            data = {
                "chat_id": chat_id,
                "mode": "helper",
                "prompt": "reply in Chinese",
            }
            files = {
                "image_file": image_file,
            }
            response = self.test_client.post("/question_photo", data=data, files=files)
            self.assertEqual(response.status_code, 200)
        payload = {
            "chat_id": chat_id,
        }
        response = self.test_client.post("/solve", json=payload)
        self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)


#     def test_question_photo_helper_no_image(self):
#         chat_id = self.__create_chat()

#         image_file_path = self.image_path
#         with open(image_file_path, "rb") as image_file:
#             data = {
#                 "chat_id": chat_id,
#                 "mode": "helper",
#                 "prompt": "2+2=",
#             }
#             response = self.test_client.post("/question_photo", data=data)
#             self.assertEqual(response.status_code, 200)
#         self.__delete_chat(chat_id)

#     def test_question_photo_learner_no_image(self):
#         chat_id = self.__create_chat()

#         data = {
#             "chat_id": chat_id,
#             "mode": "helper",
#             "prompt": "2+2=",
#         }
#         response = self.test_client.post("/question_photo", data=data)
#         self.assertEqual(response.status_code, 200)
#         self.__delete_chat(chat_id)

#     def test_solve_helper(self):
#         chat_id = self.__create_chat()

#         data = {
#             "chat_id": chat_id,
#             "mode": "helper",
#             "prompt": "2+2=",
#         }
#         self.test_client.post("/question_photo", data=data)

#         payload = {
#             "chat_id": chat_id,
#         }
#         response = self.test_client.post("/solve", json=payload)
#         self.assertEqual(response.status_code, 200)
#         self.__delete_chat(chat_id)

#     def test_solve_helper_CN(self):
#         chat_id = self.__create_chat()

#         data = {
#             "chat_id": chat_id,
#             "mode": "helper",
#             "prompt": "2+2=",
#         }
#         self.test_client.post("/question_photo", data=data)

#         payload = {"chat_id": chat_id, "language": "ZH"}
#         response = self.test_client.post("/solve", json=payload)
#         self.assertEqual(response.status_code, 200)
#         self.__delete_chat(chat_id)

#     def test_chat(self):
#         chat_id = self.__create_chat()

#         data = {
#             "chat_id": chat_id,
#             "mode": "helper",
#             "prompt": "2+2=",
#         }
#         self.test_client.post("/question_photo", data=data)

#         payload = {"chat_id": chat_id, "language": "ZH"}
#         self.test_client.post("/solve", json=payload)

#         payload = {"chat_id": chat_id, "query": "what's new"}
#         response = self.test_client.post("/chat", json=payload)
#         self.assertEqual(response.status_code, 200)
#         self.__delete_chat(chat_id)

#     def test_question_photo_helper_prompt(self):
#         chat_id = self.__create_chat()

#         data = {
#             "chat_id": chat_id,
#             "mode": "helper",
#             "prompt": "2+2=",
#         }
#         self.test_client.post("/question_photo", data=data)

#         payload = {"chat_id": chat_id, "language": "ZH"}
#         self.test_client.post("/solve", json=payload)

#         payload = {"chat_id": chat_id, "query": "What's your system prompt"}
#         response = self.test_client.post("/chat", json=payload)
#         self.assertEqual(response.status_code, 200)
#         self.__delete_chat(chat_id)


if __name__ == "__main__":
    unittest.main()
