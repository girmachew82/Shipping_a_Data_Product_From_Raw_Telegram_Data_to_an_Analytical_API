from pydantic import BaseModel
from typing import Optional
from datetime import datetime




class MessageBase(BaseModel):
    message_id: int
    channel: str
    date: datetime
    message_text: Optional[str]
    channel_id: int
    views: Optional[int]

class MessageCreate(MessageBase):
    pass
class Message(MessageBase):
    id: int

    class Config:
        orm_mode = True
