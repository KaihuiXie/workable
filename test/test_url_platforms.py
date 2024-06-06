import logging
import os
import sys
import unittest
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from src.supabase.supabase import Supabase
from src.url_platforms.supabase import UrlPlatformsSupabase


class UrlPlatformssTest(unittest.TestCase):
    supabase = None
    platform_id = None

    @classmethod
    def setUpClass(cls):
        logging.disable(level=logging.ERROR)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        cls.test_client = TestClient(app)
        cls.__init_supabase()

    @classmethod
    def tearDownClass(cls):
        ...

    @classmethod
    def __init_supabase(cls):
        load_dotenv()
        supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        cls.supabase = UrlPlatformsSupabase(supabase)

    def setUp(self):
        self.platform_id = self.__create_platform()

    def tearDown(self):
        if self.platform_id:
            self.__delete_platform(self.platform_id)

    def __create_platform(self):
        new_platform = "red"
        platform_id = self.supabase.add_new_platform(new_platform)
        return platform_id

    def __delete_platform(self, platform_id):
        self.supabase.delete_platform_by_id(platform_id)

    def test_increment_clicks(self):
        payload = {
            "platform_id": self.platform_id,
        }

        response = self.test_client.post(f"/url_platforms/increment", json=payload)
        new_clicks = self.supabase.get_clicks_by_id(self.platform_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["clicks"], 1)
        self.assertEqual(new_clicks, 1)

    def test_update_platform_id(self):
        user_id = "6e0d1fed-8845-488e-832d-4c767f0f5bb0"  # qfu@zoox18.com
        payload = {
            "user_id": user_id,
            "platform_id": self.platform_id,
        }

        response = self.test_client.post(
            f"/url_platforms/update_user_profile", json=payload
        )
        retrieved_platform_id = self.supabase.get_platform_id_by_user_id(user_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["platform_id"], self.platform_id)
        self.assertEqual(retrieved_platform_id, self.platform_id)

        # Reset records
        self.supabase.update_platform_id_in_user_profile(user_id, None)


if __name__ == "__main__":
    unittest.main()
