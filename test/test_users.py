import logging
import os
import sys
import unittest
from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app
from src.math_agent.supabase import Supabase


class UsersTest(unittest.TestCase):
    supabase = None

    @classmethod
    def setUpClass(cls):
        logging.disable(level=logging.ERROR)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        cls.test_client = TestClient(app)
        cls.__init_supabase()

    @classmethod
    def __init_supabase(cls):
        load_dotenv()
        cls.supabase = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    @classmethod
    def tearDownClass(cls):
        ...

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def __login(self, request):
        # A private method for logging in users during tests
        response = self.test_client.post("/login", json=request)
        logging.info(response.json())
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        requests = [
            {
                "email": "bowen.shawn.xiao@gmail.com",
                "phone": None,
                "password": "Shengdian123",
            },
            {"email": "bowen.shawn.xiao@gmail.com", "password": "Shengdian123"},
            {
                "email": "bowen.shawn.xiao@gmail.com",
                "phone": "1234567890",
                "password": "Shengdian123",
            },
        ]
        for request in requests:
            self.__login(request)

    def test_logout(self):
        request = {"email": "bowen.shawn.xiao@gmail.com", "password": "Shengdian123"}
        self.test_client.post("/login", json=request)
        response = self.test_client.post("/logout")
        logging.info(response.json())
        self.assertEqual(response.status_code, 200)

    def test_oauth_login(self):
        request = {"provider": "google"}
        response = self.test_client.post("/login/oauth", json=request)
        logging.info(response.json())
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        request = {"email": "test19@xxmail.com", "phone": None, "password": "test123"}
        response = self.test_client.post("/signup", json=request)
        logging.info(response.json())
        self.assertEqual(response.status_code, 200)

    def test_get_session(self):
        request = {
            "email": "bowen.shawn.xiao@gmail.com",
            "phone": None,
            "password": "Shengdian123",
        }
        self.__login(request)
        response = self.test_client.get("/session")
        logging.info(response.json())
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
