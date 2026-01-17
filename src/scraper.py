import os
import json
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

load_dotenv()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Setup logging
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
log_file = "logs/scraper.log"

# Rotating file handler: 5MB per file, keep 5 backups
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)

# Stream handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION = os.getenv("TELEGRAM_SESSION")

DATA_DIR = "data/raw/telegram_messages"

CHANNELS = [
    "https://t.me/CheMed123",
    "https://t.me/tikvahpharma",
    "https://t.me/lobelia4cosmetics",
    "https://t.me/Thequorachannel"
]

def extract_message_data(msg, channel_name, img_path=None):
    """
    Explicitly shapes the message data into a dictionary.
    """
    return {
        "id": msg.id,
        "channel_name": channel_name,
        "date": msg.date.isoformat() if msg.date else None,
        "message": msg.message,
        "sender_id": msg.sender_id,
        "reply_to_msg_id": msg.reply_to_msg_id if msg.reply_to else None,
        "media_path": img_path,
        "views": getattr(msg, 'views', None),
        "forwards": getattr(msg, 'forwards', None),
        "edit_date": msg.edit_date.isoformat() if getattr(msg, 'edit_date', None) else None,
        "post_author": getattr(msg, 'post_author', None),
        "grouped_id": getattr(msg, 'grouped_id', None),
    }

async def scrape_channel(client, channel_url):
    channel_name = channel_url.split("/")[-1]
    today = datetime.today().strftime("%Y-%m-%d")
    folder_path = os.path.join(DATA_DIR, today, channel_name)
    os.makedirs(folder_path, exist_ok=True)

    messages = []
    logging.info(f"🚀 Starting scrape for {channel_name} (Date: {today})")

    try:
        async for msg in client.iter_messages(channel_url, limit=10000):
            try:
                img_path = None
                # Save image if it exists
                if isinstance(msg.media, MessageMediaPhoto):
                    img_filename = f"{msg.id}.jpg"
                    img_path = os.path.join(folder_path, img_filename)
                    # Download if not exists
                    if not os.path.exists(img_path):
                        await client.download_media(msg.media, file=img_path)

                # Explicitly shape the data
                msg_data = extract_message_data(msg, channel_name, img_path)
                messages.append(msg_data)

            except Exception as e:
                logging.warning(f"⚠️ Error processing message {msg.id} in {channel_name}: {e}")

        # Save all messages to a JSON file
        json_path = os.path.join(folder_path, "messages.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

        logging.info(f"✅ Scraped {len(messages)} messages from {channel_name}")

    except Exception as e:
        logging.error(f"❌ Critical error scraping {channel_name}: {e}")
        raise e

async def main():
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        for channel in CHANNELS:
            try:
                await scrape_channel(client, channel)
            except Exception as e:
                logging.error(f"❌ Failed scraping {channel}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
