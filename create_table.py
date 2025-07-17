import os
import json
import pandas as pd
import psycopg2
import re

from datetime import datetime

# Set your data folder
DATA_FOLDER = "data/raw/telegram_messages/2025-07-13/"

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="telegram_data",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Helper: Extract fields from each message
def extract_message_fields(message, channel_name):
    message_text = message.get('message', '')
    url_match = re.search(r'https?://\S+', message_text)
    phone_match = re.search(r'\+251\s?\d+', message_text)

    media = message.get("media", {})
    photo = media.get("photo", {}) if media else {}
    sizes = photo.get("sizes", []) if photo else []

    return {
        "channel": channel_name,
        "message_id": message.get("id"),
        "channel_id": message.get("peer_id", {}).get("channel_id"),
        "message_text": message_text,
        "date": message.get("date"),
        "views": message.get("views"),
        "forwards": message.get("forwards"),
        "edit_date": message.get("edit_date"),
        "url": url_match.group(0) if url_match else None,
        "phone_number": phone_match.group(0) if phone_match else None,
        "image_sizes": json.dumps(sizes)
    }

# Process all JSON files into a DataFrame
rows = []
for filename in os.listdir(DATA_FOLDER):
    if filename.endswith(".json"):
        filepath = os.path.join(DATA_FOLDER, filename)
        channel_name = os.path.splitext(filename)[0]  # filename without .json

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for message in data:
                    rows.append(extract_message_fields(message, channel_name))
            else:
                print(f"⚠️ Unexpected format in {filename}, skipping.")

df = pd.DataFrame(rows)
print("🔍 Preview:\n", df.head())
def safe_int(val):
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None
# Insert into Postgres
count = 0
for _, row in df.iterrows():
    try:
        cur.execute("""
            INSERT INTO raw_data.tgram_messages (
                channel, message_id, channel_id, message_text, date,
                views, forwards, edit_date, url, phone_number, image_sizes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['channel'],
            safe_int(row['message_id']),
            safe_int(row['channel_id']),
            row['message_text'],
            row['date'],
            safe_int(row['views']),
            safe_int(row['forwards']),
            row['edit_date'],
            row['url'],
            row['phone_number'],
            row['image_sizes']
        ))
        count += 1

    except Exception as e:
        conn.rollback()
        print("Failed row ", row)
        print("Error ",e)
        continue
conn.commit()
cur.close()
conn.close()

print("✅ All records inserted with channel info.", count)
