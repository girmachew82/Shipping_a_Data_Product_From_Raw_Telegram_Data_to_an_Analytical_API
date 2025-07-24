from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class MessageCreate(BaseModel):
    channel: str
    message_id: int
    channel_id: int
    message_text: Optional[str]
    date: Optional[datetime]
    views: Optional[int]
    forwards: Optional[int] = 0
    edit_date: Optional[datetime] = None
    url: Optional[str]
    phone_number: Optional[str]
    image_sizes:  Optional[List[Dict[str, Any]]] = None
    
class MessageResponse(MessageCreate):
    id: int

    class Config:
        orm_mode = True
