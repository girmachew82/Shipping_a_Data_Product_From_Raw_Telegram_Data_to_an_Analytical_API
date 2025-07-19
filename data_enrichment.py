import os
import re
import cv2
import psycopg2
import easyocr
from ultralytics import YOLO
from datetime import datetime

# === PostgreSQL DB Connection Settings ===
DB_CONFIG = {
    "dbname": "telegram_data",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

# === Directories to Process ===
directories = [
    "data/raw/telegram_images/CheMed123/2025-07-13",
    "data/raw/telegram_images/lobelia4cosmetics/2025-07-13"
]

def extract_message_id(filename):
    match = re.search(r'message_(\d+)_photo', filename)
    return int(match.group(1)) if match else None

# === Initialize Models ===
reader = easyocr.Reader(['en'])               # OCR Reader
model = YOLO("yolov8n.pt")                    # Object detection model (COCO pretrained)

# === Classification Logic Based on OCR Text ===
def classify_text(texts):
    text = " ".join(texts).lower()
    if "vitamin" in text:
        return "vitamins"
    elif "promotion" in text or "new arrival" in text:
        return "promotion"
    elif "pill" in text or "capsule" in text:
        return "pills"
    elif "drug" in text or "tablet" in text:
        return "drug"
    return "unknown"
def extract_price(texts):
    for text in texts:
        # Normalize common formats
        clean_text = text.replace(",", "").lower()

        # Match formats like "2459 ብር", "2459 birr", "35.00 ETB", "1,200.00 birr"
        match = re.search(r'(\d+(?:\.\d{1,2})?)\s*(etb|birr|ብር)', clean_text)
        if match:
            return f"{match.group(1)} ETB"
    return "N/A"
# === Connect to PostgreSQL ===
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# === Process Images ===
for dir_path in directories:
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)

        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        print(f"Processing: {file_path}")

        # Load image and convert to grayscale for EasyOCR
        img = cv2.imread(file_path)
        if img is None:
            print(f"⚠️ Failed to read image: {file_path}")
            continue

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # OCR Detection
        ocr_result = reader.readtext(img_gray)
        texts = [item[1] for item in ocr_result]

        # Extract price and drug name
        price = extract_price(texts)
        drug_name = next((t for t in texts if t.isupper() and len(t) > 4), "N/A")

        # Classification via text rules
        detected_class = classify_text(texts)
        confidence_score = 1.0 if detected_class != "unknown" else 0.0
        # Extract message_id from filename
        message_id = extract_message_id(filename)
        # Insert into database
        try:
            cursor.execute("""
                INSERT INTO raw_data.image_detection (
                    image_path, drug_name, price, detected_class, confidence_score, created_at, message_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (file_path, drug_name, price, detected_class, confidence_score, datetime.now(), message_id))
            conn.commit()
            print(f"✅ Inserted: {filename} → Class: {detected_class} (MsgID: {message_id})")
        except Exception as e:
            print(f"❌ DB Insert Error: {e}")

# === Close DB connection ===
cursor.close()
conn.close()
