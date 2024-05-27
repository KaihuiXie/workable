import logging
import os
import sys
import time
import unittest
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from src.credits.supabase import CreditsSupabase
from src.math_agent.supabase import Supabase


class CreditsTest(unittest.TestCase):
    user_id = "88257e09-ce6f-4165-bc34-31bf0c873f29"  # lck2048@gmail.com
    supabase = None

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
        cls.supabase = CreditsSupabase(
            Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        )

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_credit(self):

        response = self.test_client.get(f"/credit/{self.user_id}")
        logging.error(response.json())
        assert response.status_code == 200

    def test_get_temp_credit(self):
        response = self.test_client.get(f"/credit/temp/{self.user_id}")
        logging.error(response.json())
        assert response.status_code == 200

    def test_get_perm_credit(self):
        response = self.test_client.get(f"/credit/perm/{self.user_id}")
        logging.error(response.json())
        assert response.status_code == 200

    def test_decrement_credit(self):
        credit_amount = 100
        payload = {
            "user_id": self.user_id,
            "credit": credit_amount,
        }
        self.test_client.put("/credit/temp", json=payload)
        payload = {
            "user_id": self.user_id,
        }
        response = self.test_client.put("/credit", json=payload)
        logging.error(response.json())
        assert response.status_code == 200

    def test_credit(self):
        response = self.test_client.get(f"/credit/{self.user_id}")
        logging.error(response.json())
        assert response.status_code == 200

    def test_create_credit(self):
        self.supabase.delete_credit(self.user_id)
        response = self.test_client.post(f"/credit/{self.user_id}")
        logging.error(response.json())
        assert response.status_code == 200
        time.sleep(1)

    def test_update_temp_credit(self):
        credit_amount = 100
        payload = {
            "user_id": self.user_id,
            "credit": credit_amount,
        }
        response = self.test_client.put("/credit/temp", json=payload)
        logging.error(response.json())
        assert response.status_code == 200

    def test_update_perm_credit(self):
        credit_amount = 100
        payload = {
            "user_id": self.user_id,
            "credit": credit_amount,
        }
        response = self.test_client.put("/credit/perm", json=payload)
        logging.error(response.json())
        assert response.status_code == 200


if __name__ == "__main__":
    unittest.main()
