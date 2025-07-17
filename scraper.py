import os
import json
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
import base64 
import pandas  as pd
# ==============================================================================
# CONFIGURATION
# ==============================================================================

#  Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAPM_API_HASH')
PHONE_NUMBER = '+251963188009'

# List of Telegram channel usernames to scrape.
CHANNELS = [
    'https://t.me/CheMed123',
    'https://t.me/lobelia4cosmetics',
    'https://t.me/tikvahpharma',
]
# Output directories
BASE_DATA_DIR = 'data/raw/telegram_messages'
BASE_IMAGE_DIR = 'data/raw/telegram_images'

# SCRAPING LIMITS
MAX_MESSAGES_PER_CHANNEL = 50
MAX_PHOTOS_PER_CHANNEL = 50

# ==============================================================================
# LOGGING SETUP
# ==============================================================================

def setup_logging():
    """Sets up robust logging for the scraping process."""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/scraping.log'),
            logging.StreamHandler()
        ]
    )
    logging.info('Logging has been set up.')

# ==============================================================================
# DATA SCRAPING FUNCTIONS
# ==============================================================================

async def scrape_channel(client, channel_username, min_id=0):
    """
    Scrapes a limited number of messages and photos from a single channel.
    
    Args:
        client (TelegramClient): The authenticated Telethon client.
        channel_username (str): The username or URL of the channel.
        min_id (int): The minimum message ID to scrape from (for incremental updates).
    
    Returns:
        list: A list of dictionaries, where each dictionary represents a message.
    """
    try:
        logging.info(f"Scraping from channel: {channel_username} with message limit {MAX_MESSAGES_PER_CHANNEL} and photo limit {MAX_PHOTOS_PER_CHANNEL}")
        
        all_messages = []
        downloaded_photos = 0
        
        # We use a limit here to prevent fetching the entire channel history at once.
        async for message in client.iter_messages(channel_username, min_id=min_id, limit=MAX_MESSAGES_PER_CHANNEL):
            message_dict = message.to_dict()
            all_messages.append(message_dict)
            
            # Check for media (images) and download them if the photo limit has not been reached.
            if message.photo:
                if downloaded_photos < MAX_PHOTOS_PER_CHANNEL:
                    await download_image(client, message)
                    downloaded_photos += 1
                else:
                    logging.info(f"Photo limit reached for {channel_username}. Skipping further image downloads.")

        logging.info(f"Successfully scraped {len(all_messages)} new messages from {channel_username}.")
        return all_messages
    except Exception as e:
        logging.error(f"Error scraping channel {channel_username}: {e}")
        return []

async def download_image(client, message):
    """
    Downloads an image from a message.
    """
    try:
        channel_name = message.chat.username or str(message.chat.id)
        current_date = datetime.now().strftime('%Y-%m-%d')
        image_path = os.path.join(BASE_IMAGE_DIR, channel_name, current_date)
        os.makedirs(image_path, exist_ok=True)
        
        image_filename = f'message_{message.id}_photo.jpg'
        await client.download_media(message, file=os.path.join(image_path, image_filename))
        logging.info(f"Downloaded image from message {message.id} in {channel_name}.")
    except Exception as e:
        logging.error(f"Error downloading image from message {message.id}: {e}")

# ==============================================================================
# DATA STORAGE FUNCTIONS (DATA LAKE)
# ==============================================================================

class DateTimeBytesEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that handles datetime objects and bytes objects.
    """
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            # Encode bytes to a Base64 string to make it JSON serializable
            return base64.b64encode(o).decode('utf-8')
        return super().default(o)

def save_data(data, channel_username):
    """
    Stores scraped data in a structured, partitioned directory.
    
    Args:
        data (list or dict): The data to save.
        channel_username (str): The name of the channel.
    """
    if not data:
        logging.warning(f"No data to save for channel {channel_username}.")
        return

    try:
        # Create a partitioned directory structure
        current_date = datetime.now().strftime('%Y-%m-%d')
        channel_name = channel_username.replace('https://t.me/', '')
        
        data_dir = os.path.join("data/raw/telegram_messages", current_date)
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, f'{channel_name}.json')
        
        # Read existing data to append if file already exists
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    logging.warning(f"File {file_path} is empty or corrupted. Overwriting.")
                    
        # Merge new and existing data
        new_ids = {msg['id'] for msg in data}
        combined_data = [msg for msg in existing_data if msg['id'] not in new_ids] + data
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Use the custom encoder to handle both datetime and bytes objects
            json.dump(combined_data, f, ensure_ascii=False, indent=4, cls=DateTimeBytesEncoder)
        
        logging.info(f"Saved {len(data)} new messages to {file_path}")
            
    except Exception as e:
        logging.error(f"Failed to save data for channel {channel_username}: {e}")

# ==============================================================================
# MAIN EXECUTION SCRIPT
# ==============================================================================

async def main():
    setup_logging()
    logging.info("Starting Telegram scraping process...")
    
    client = TelegramClient('my_session', API_ID, API_HASH)
    
    await client.start(phone=PHONE_NUMBER)
    logging.info("Client connected and authenticated.")
    
    for channel_url in CHANNELS:
        channel_name = channel_url.split('/')[-1]
        
        # Determine the latest message ID for incremental scraping
        data_dir = os.path.join(BASE_DATA_DIR, datetime.now().strftime('%Y-%m-%d'))
        file_path = os.path.join(data_dir, f'{channel_name}.json')
        min_id = 0
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if existing_data:
                        min_id = max(msg['id'] for msg in existing_data)
                except (json.JSONDecodeError, ValueError):
                    pass # Start from scratch if file is empty or corrupted
        
        scraped_messages = await scrape_channel(client, channel_url, min_id)
        if scraped_messages:
            save_data(scraped_messages, channel_url)
            
    await client.run_until_disconnected()
    logging.info("Scraping process finished.")

if __name__ == '__main__':
    asyncio.run(main())