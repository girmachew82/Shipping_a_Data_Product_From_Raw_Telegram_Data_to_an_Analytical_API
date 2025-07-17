import os
import json
import psycopg2
from ultralytics import YOLO
from PIL import Image
import re

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="telegram_data",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  


IMAGE_DIR = "data/raw/telegram_images/CheMed123/2025-07-13/" 

# Loop through image files
for filename in os.listdir(IMAGE_DIR):
    if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        continue

    image_path = os.path.join(IMAGE_DIR, filename)
    match = re.search(r'message_(\d+)_photo', filename)
    if match:
        message_id = int(match.group(1))
    else:
        print(f"Skipping malformed filename: {filename}")
        continue
    # Run object detection
    results = model(image_path)

    for result in results:
        boxes = result.boxes

        for box in boxes:
            cls = result.names[int(box.cls[0])]
            score = float(box.conf[0])
            
            # Insert into detections table
            cur.execute("""
                INSERT INTO raw_data.fct_image_detections (message_id, detected_object_class, confidence_score)
                VALUES (%s, %s, %s)
            """, (message_id, cls, score))

    print(f"Processed {filename}")

conn.commit()
conn.close()
print("Detection complete.")
