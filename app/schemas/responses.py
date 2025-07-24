from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TopProductResponse(BaseModel):
    product_name: Optional[str]
    mention_count: Optional[int]

class ChannelActivityResponse(BaseModel):
    date: Optional[str]
    message_count: Optional[int]

class MessageSearchResult(BaseModel):
    message_id: Optional[int]
    channel: Optional[str]
    date: Optional[datetime]
    message_text: Optional[str]
    channel_id: Optional[int]
    views: Optional[int]
