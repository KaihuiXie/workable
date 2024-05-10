from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel


class CreateSharedChatRequest(BaseModel):
    chat_id: str
    is_permanent: Optional[bool] = True
