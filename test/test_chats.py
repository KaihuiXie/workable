import os
import json
import sys
import logging
import unittest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from pathlib import Path

from api.main import app
from src.math_agent.supabase import Supabase
from src.math_agent.math_agent import MathAgent
from common.constants import ROOT_DIR


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
        cls.supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    @classmethod
    def __init_math_agent(cls):
        load_dotenv()
        cls.math_agent = MathAgent(
            os.getenv("OPENAI_API_KEYS"), os.getenv("WOLFRAM_ALPHA_APP_ID")
        )

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def __create_chat(self):
        chat_id = self.supabase.create_empty_chat(self.user_id)
        return chat_id

    def __delete_chat(self, chat_id):
        self.supabase.delete_chat_by_id(chat_id)

    def test_new_chat_id(self):
        data = {
            "user_id": self.user_id,
        }
        response = self.test_client.post("/new_chat_id", json=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.load(response)
        chat_id = response_json["chat_id"]
        self.__delete_chat(chat_id)

    def test_question_photo_learner_no_photo(self):
        data = {
            "user_id": self.user_id,
        }
        response = self.test_client.post("/new_chat_id", json=data)
        self.assertEqual(response.status_code, 200)
        response_json = json.load(response)
        chat_id = response_json["chat_id"]
        data = {"chat_id": chat_id, "mode": "learner", "prompt": "1+1=?"}
        response = self.test_client.post("/question_photo", data=data)
        self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_get_chat(self):
        chat_id = self.__create_chat()
        response = self.test_client.get(f"/chat/{chat_id}")
        self.assertEqual(response.status_code, 200)
        response_json = json.load(response)
        self.assertEqual(response_json["payload"], "")
        self.assertEqual(response_json["question"], "")
        self.assertEqual(response_json["image_str"], "")
        self.__delete_chat(chat_id)

    # def test_all_chats(self):
    #     chat_id_1 = self.__create_chat()
    #     chat_id_2 = self.__create_chat()
    #
    #     response = self.test_client.get(f"/all_chats/{self.user_id}")
    #     self.assertEqual(response.status_code, 200)
    #     response_json = json.load(response)
    #     ids = [item["id"] for item in response_json["data"]]
    #     self.assertEqual(set(ids), set({chat_id_1, chat_id_2}))
    #     self.__delete_chat(chat_id_1)
    #     self.__delete_chat(chat_id_2)

    def test_question_photo_learner_no_prompt(self):
        chat_id = self.__create_chat()

        image_file_path = self.image_path
        with open(image_file_path, "rb") as image_file:
            data = {
                "chat_id": chat_id,
                "mode": "learner",
            }
            files = {
                "image_file": image_file,
            }
            response = self.test_client.post("/question_photo", data=data, files=files)
            self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_question_photo_helper_no_prompt(self):
        chat_id = self.__create_chat()

        image_file_path = self.image_path
        with open(image_file_path, "rb") as image_file:
            data = {
                "chat_id": chat_id,
                "mode": "helper",
            }
            files = {
                "image_file": image_file,
            }
            response = self.test_client.post("/question_photo", data=data, files=files)
            self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_question_photo_learner_prompt(self):
        chat_id = self.__create_chat()

        image_file_path = self.image_path
        with open(image_file_path, "rb") as image_file:
            data = {
                "chat_id": chat_id,
                "mode": "learner",
                "prompt": "reply in Chinese",
            }
            files = {
                "image_file": image_file,
            }
            response = self.test_client.post("/question_photo", data=data, files=files)
            self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_question_photo_helper_prompt(self):
        chat_id = self.__create_chat()

        image_file_path = self.image_path
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
        self.__delete_chat(chat_id)

    def test_question_photo_helper_no_image(self):
        chat_id = self.__create_chat()

        image_file_path = self.image_path
        with open(image_file_path, "rb") as image_file:
            data = {
                "chat_id": chat_id,
                "mode": "helper",
                "prompt": "2+2=",
            }
            response = self.test_client.post("/question_photo", data=data)
            self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_question_photo_learner_no_image(self):
        chat_id = self.__create_chat()

        data = {
            "chat_id": chat_id,
            "mode": "helper",
            "prompt": "2+2=",
        }
        response = self.test_client.post("/question_photo", data=data)
        self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_solve_helper(self):
        chat_id = self.__create_chat()

        data = {
            "chat_id": chat_id,
            "mode": "helper",
            "prompt": "2+2=",
        }
        self.test_client.post("/question_photo", data=data)

        payload = {
            "chat_id": chat_id,
        }
        response = self.test_client.post("/solve", json=payload)
        self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_solve_helper_CN(self):
        chat_id = self.__create_chat()

        data = {
            "chat_id": chat_id,
            "mode": "helper",
            "prompt": "2+2=",
        }
        self.test_client.post("/question_photo", data=data)

        payload = {"chat_id": chat_id, "language": "ZH"}
        response = self.test_client.post("/solve", json=payload)
        self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)

    def test_chat(self):
        chat_id = self.__create_chat()

        data = {
            "chat_id": chat_id,
            "mode": "helper",
            "prompt": "2+2=",
        }
        self.test_client.post("/question_photo", data=data)

        payload = {"chat_id": chat_id, "language": "ZH"}
        self.test_client.post("/solve", json=payload)

        payload = {"chat_id": chat_id, "query": "what's new"}
        response = self.test_client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        self.__delete_chat(chat_id)


if __name__ == "__main__":
    unittest.main()
