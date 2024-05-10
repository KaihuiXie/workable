import logging
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app


class InvitationsTest(unittest.TestCase):
    chat_id = None
    supabase = None

    @classmethod
    def setUpClass(cls):
        logging.disable(level=logging.ERROR)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        cls.test_client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        ...

    def setUp(self):
        ...

    def tearDown(self):
        ...

    # With an exist, and not expired token.
    # Will return true, and the referrer_id
    def test_get_referrer_success_case(self):
        invitation_token = "c99770af-f316-4377-ad28-a65c032e03ee"

        response = self.test_client.get(f"/referrer/{invitation_token}")
        logging.error(response.json())
        assert response.status_code == 200

    # With a random token that does not exist
    # will return false, and an empty referrer_id
    def test_get_referrer_wrong_token_case(self):
        invitation_token = "3d9e633f-542b-47ab-9606"

        response = self.test_client.get(f"/referrer/{invitation_token}")
        logging.error(response.json())
        assert response.status_code == 200

    # need to use a expired token
    # will return false, and a referrer id.
    # So that front end can create an alert for user to ask for referrer to refresh token
    def test_get_referrer_expire_case(self):
        invitation_token = "36993590-7a33-4fc6-944f-1ad0a6b63782"

        response = self.test_client.get(f"/referrer/{invitation_token}")
        logging.error(response.json())
        assert response.status_code == 200

    # for create a new token case: need to use a new user_id that doesn't have a invitation token
    # for getting existing token case: need to use a user_id that have a not expired token
    # for expired case: need to use a user_id that has an expired token
    def test_get_invitation_success_case(self):
        user_id = "a4804bea-93d8-4789-969d-19b5364f7436"
        response = self.test_client.get(f"/invitation/{user_id}")
        logging.error(response.json())
        assert response.status_code == 200


if __name__ == "__main__":
    unittest.main()
