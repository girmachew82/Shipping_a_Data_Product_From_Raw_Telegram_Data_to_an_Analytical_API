import psycopg2
from dagster import op

@op
def load_raw_to_postgres(context, scraped_data: list):
    conn = psycopg2.connect(
        dbname="telegram_data",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    for msg in scraped_data:
        cur.execute("""
            INSERT INTO raw_data.gram_messages (
                channel, message_id, channel_id, message_text, date, views, 
                forwards, edit_date, url, phone_number, image_sizes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id, channel_id) DO NOTHING;
        """, (
            msg["channel"], msg["message_id"], msg["channel_id"], msg["message_text"],
            msg["date"], msg["views"], msg["forwards"], msg["edit_date"],
            msg["url"], msg["phone_number"], msg["image_sizes"]
        ))

    conn.commit()
    cur.close()
    conn.close()
    context.log.info(f"Inserted {len(scraped_data)} messages into DB.")
