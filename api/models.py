from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, unique=True)
    channel = Column(String)
    date = Column(DateTime)
    message_text = Column(Text)
    channel_id = Column(Integer)
    views = Column(Integer)


