from datetime import datetime
from enum import IntEnum
from pydantic import BaseModel
from typing import Optional


class CreateSharedChatRequest(BaseModel):
    chat_id: str
    is_permanent: Optional[bool] = True
