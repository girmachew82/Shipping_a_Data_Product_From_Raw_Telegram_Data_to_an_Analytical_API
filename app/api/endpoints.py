from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.message import TgramMessage
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.responses import TopProductResponse, ChannelActivityResponse
from typing import List
from datetime import date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/messages/", response_model=MessageResponse)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    db_msg = TgramMessage(**message.dict())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

@router.get("/messages/", response_model=list[MessageResponse])
def get_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TgramMessage).offset(skip).limit(limit).all()

@router.get("/channels/{channel_name}/activity", response_model=ChannelActivityResponse)
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    count = db.query(TgramMessage).filter(TgramMessage.channel == channel_name).count()
    return {
            "channel": channel_name, 
            "message_count": count,
            "date": date.today().isoformat()
            }

@router.get("/search/messages", response_model=list[MessageResponse])
def search_messages(query: str, db: Session = Depends(get_db)):
    return db.query(TgramMessage).filter(TgramMessage.message_text.ilike(f"%{query}%")).all()

@router.get("/reports/top-products", response_model=List[TopProductResponse])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    from sqlalchemy import func
    result = (
        db.query(TgramMessage.message_text)
        .filter(TgramMessage.message_text.ilike("%paracetamol%"))
        .limit(limit)
        .all()
    )
    return [{"product_name": "paracetamol", "mention_count": len(result)}]
