import os
import json
import psycopg2
import glob
from datetime import datetime
import logging


# Database connection details
DB_NAME ="telegram_data"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432
RAW_DATA_DIR = 'data/raw/telegram_messages'

def load_data_to_db():
    conn = None
    try:
        logging.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        # 1. Create the schema and table if they don't exist
        print("Creating raw schema and telegram_messages table...")
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw_data;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_data.telegram_messages (
                raw_json jsonb
            );
        """)
        conn.commit()
        
        # 2. Iterate through all JSON files and load them
        json_files = glob.glob(f"{RAW_DATA_DIR}/**/*.json", recursive=True)
        
        if not json_files:
            print("No JSON files found in the raw data directory.")
            return

        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    
                    print(f"Loading {len(messages)} messages from {file_path}...")
                    
                    # Prepare data for bulk insertion
                    data_to_insert = [(json.dumps(msg),) for msg in messages]
                    
                    # Insert data into the table
                    cur.executemany("INSERT INTO raw_data.telegram_messages (raw_json) VALUES (%s::jsonb);", data_to_insert)
                    conn.commit()

            except (IOError, json.JSONDecodeError) as e:
                print(f"Error processing file {file_path}: {e}")
                conn.rollback()

        print("Data loading complete.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
    finally:
        if conn:
            conn.close()
            print("PostgreSQL connection is closed.")

if __name__ == "__main__":
    load_data_to_db()