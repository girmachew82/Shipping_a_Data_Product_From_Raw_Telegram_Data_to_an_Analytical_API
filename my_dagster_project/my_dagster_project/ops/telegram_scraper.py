from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from dagster import op, Out, Output
from datetime import datetime
import os
import json

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")  

CHANNEL_USERNAMES = [
    'CheMed123',
    'lobelia4cosmetics',
    'tikvahpharma',
]

@op(out=Out())
def scrape_telegram_data(context):
    client = TelegramClient("anon", API_ID, API_HASH)
    messages = []

    with client:
        for username in CHANNEL_USERNAMES:
            entity = client.get_entity(username)
            history = client(GetHistoryRequest(
                peer=entity,
                limit=100,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            for msg in history.messages:
                data = {
                    "channel": username,
                    "message_id": msg.id,
                    "channel_id": entity.id,
                    "message_text": msg.message,
                    "date": msg.date.isoformat(),
                    "views": msg.views,
                    "forwards": msg.forwards,
                    "edit_date": msg.edit_date.isoformat() if msg.edit_date else None,
                    "url": f"https://t.me/{username}/{msg.id}",
                    "phone_number": getattr(msg.from_id, 'user_id', None),
                    "image_sizes": json.dumps([{
                        "width": attr.w,
                        "height": attr.h
                    } for attr in getattr(msg.media, 'photo', {}).sizes]) if hasattr(msg.media, 'photo') else None
                }
                messages.append(data)

    context.log.info(f"Scraped {len(messages)} messages.")
    return messages
