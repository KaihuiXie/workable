import os
from datetime import timedelta

EVERY_DAY_CREDIT_INCREMENT = 5
COST_PER_QUESTION = 1
DEFAULT_CREDIT = 0
INVITATION_TOKEN_EXPIRATION = 36500
INVITATION_BONUS = 20
MAX_MESSAGE_SIZE = 15
SHARED_CHAT_EXPIRE_TIME = timedelta(days=30)
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"  # example: '2024-04-03T04:14:44.818639+00:00'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
