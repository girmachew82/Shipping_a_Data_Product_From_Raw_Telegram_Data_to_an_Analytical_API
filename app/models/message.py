from sqlalchemy import Column, Integer, String, BigInteger, DateTime, JSON, Text
from sqlalchemy.schema import MetaData
from app.db.database import Base

schema_metadata = MetaData(schema="raw_data")

class TgramMessage(Base):
    __tablename__ = "tgram_messages"
    __table_args__ = {'schema': 'raw_data'}

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String)
    message_id = Column(BigInteger, index=True)
    channel_id = Column(BigInteger)
    message_text = Column(Text, nullable=True)
    date = Column(DateTime)
    views = Column(BigInteger, nullable=True)
    forwards = Column(BigInteger, nullable=True)
    edit_date = Column(DateTime, nullable=True)
    url = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    image_sizes = Column(JSON, nullable=True)
