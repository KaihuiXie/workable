import sys
import logging
import unittest
from fastapi.testclient import TestClient
from pathlib import Path
from api.main import app


class UsersTest(unittest.TestCase):
    chat_id = None
    supabase = None

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.INFO)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        cls.test_client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        ...

    def setUp(self):
        ...

    def tearDown(self):
        ...
