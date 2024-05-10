import logging
import os
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from common.constants import SHARED_CHAT_EXPIRE_TIME
from src.math_agent.supabase import Supabase


class SharedChatsTest(unittest.TestCase):
    chat_id = None
    supabase = None

    @classmethod
    def setUpClass(cls):
        logging.disable(level=logging.ERROR)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        cls.test_client = TestClient(app)
        cls.__init_supabase()
        cls.__create_chat()

    @classmethod
    def tearDownClass(cls):
        cls.__delete_chat()

    @classmethod
    def __init_supabase(cls):
        load_dotenv()
        cls.supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    @classmethod
    def __create_chat(cls):
        user_id = "88257e09-ce6f-4165-bc34-31bf0c873f29"  # lck2048@gmail.com
        cls.chat_id = cls.supabase.create_empty_chat(user_id)

    @classmethod
    def __delete_chat(cls):
        cls.supabase.delete_chat_by_id(cls.chat_id)

    def setUp(self):
        ...

    def tearDown(self):
        self.supabase.delete_shared_chat_by_chat_id(self.chat_id)

    def test_create_shared_chat(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        logging.info(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.__get_shared_chat_count(), 1)

    def test_create_shared_chat_multiple_times_with_same_version(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(response.status_code, 200)
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(response.status_code, 200)
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.__get_shared_chat_count(), 1)

    def test_create_shared_chat_multiple_times_with_different_versions(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(response.status_code, 200)

        self.__update_chat_thumbnail("thumbnail 1")
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(response.status_code, 200)

        self.__update_chat_thumbnail("thumbnail 2")
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.__get_shared_chat_count(), 3)

    def test_get_shared_chat(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        shared_chat_id = response.text.strip('"')
        response = self.test_client.get(f"/shared_chat/{shared_chat_id}")
        self.assertEqual(response.status_code, 200)

    def test_delete_shared_chat_by_shared_chat_id(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(self.__get_shared_chat_count(), 1)
        shared_chat_id = response.text.strip('"')
        response = self.test_client.delete(
            f"/shared_chat/by_shared_chat_id/{shared_chat_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.__get_shared_chat_count(), 0)

    def test_delete_shared_chat_by_chat_id(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        self.test_client.post(f"/shared_chat/create", json=request)
        self.__update_chat_thumbnail("thumbnail 1")
        self.test_client.post(f"/shared_chat/create", json=request)
        self.__update_chat_thumbnail("thumbnail 2")
        self.test_client.post(f"/shared_chat/create", json=request)
        self.assertEqual(self.__get_shared_chat_count(), 3)

        response = self.test_client.delete(f"/shared_chat/by_chat_id/{self.chat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.__get_shared_chat_count(), 0)

    def test_update_create_time(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        shared_chat_id_1 = response.text.strip('"')
        response = self.__get_shared_chat(shared_chat_id_1)
        created_at_1 = response["created_at"]

        time.sleep(1)
        response = self.test_client.post(f"/shared_chat/create", json=request)
        shared_chat_id_2 = response.text.strip('"')
        response = self.__get_shared_chat(shared_chat_id_2)
        created_at_2 = response["created_at"]

        self.assertEqual(shared_chat_id_1, shared_chat_id_2)
        self.assertNotEqual(created_at_1, created_at_2)

    def test_shared_chat_expired(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": False,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.__update_shared_chat_create_time(response.text.strip('"'))
        self.assertEqual(self.__get_shared_chat_count(), 1)

        time.sleep(1)
        shared_chat_id = response.text.strip('"')
        response = self.test_client.get(f"/shared_chat/{shared_chat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.strip('"'), "null")
        self.assertEqual(self.__get_shared_chat_count(), 0)

    def test_permanent_shared_chat_expired(self):
        request = {
            "chat_id": self.chat_id,
            "is_permanent": True,
        }
        response = self.test_client.post(f"/shared_chat/create", json=request)
        self.__update_shared_chat_create_time(response.text.strip('"'))
        time.sleep(1)
        shared_chat_id = response.text.strip('"')
        response = self.test_client.get(f"/shared_chat/{shared_chat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.text.strip('"'), "null")
        self.assertEqual(self.__get_shared_chat_count(), 1)

    def __get_shared_chat_count(self):
        response = self.supabase.get_shared_chats_by_chat_id(self.chat_id)
        return len(response)

    def __get_shared_chat(self, shared_chat_id: str):
        response = self.supabase.get_shared_chat_by_shared_chat_id(shared_chat_id)
        return response

    def __update_chat_thumbnail(self, thumbnail: str):
        self.supabase.update_thumbnail(self.chat_id, thumbnail)

    def __update_shared_chat_create_time(self, shared_chat_id: str):
        updated_at = (datetime.now(timezone.utc) - SHARED_CHAT_EXPIRE_TIME).strftime(
            "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        self.supabase.update_shared_chat_create_time(shared_chat_id, updated_at)


if __name__ == "__main__":
    unittest.main()
