import requests
import re
import os
from bs4 import BeautifulSoup
from pyrogram import Client, filters

# Telegram Bot Credentials (Replace these values)
API_ID = int(os.getenv("API_ID"))  # Ensure it's an integer
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot Initialization
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to Extract Direct Download Link from TeraBox
def get_terabox_download_link(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }

    session = requests.Session()
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all("script")

        for script in script_tags:
            if "download" in script.text:
                match = re.search(r'"(https://[^\s]+?download.*?)"', script.text)
                if match:
                    return match.group(1)  # Return direct download link
    return None

# Function to Download the File from TeraBox
def download_from_terabox(url):
    download_link = get_terabox_download_link(url)
    
    if not download_link:
        return None

    file_name = "downloaded_file.zip"  # Default filename
    response = requests.get(download_link, stream=True)

    with open(file_name, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    return file_name  # Return the downloaded file path

# Telegram Bot Handlers
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("👋 Welcome to TeraBox Downloader Bot!\n\nSend me a TeraBox link to download the file.")

@app.on_message(filters.text)
def process_link(client, message):
    url = message.text.strip()
    
    if "terabox.com" in url:
        message.reply_text("🔍 Processing your link, please wait...")
        
        file_path = download_from_terabox(url)
        
        if file_path:
            message.reply_document(file_path, caption="✅ Here is your downloaded file!")
            os.remove(file_path)  # Delete the file after sending
        else:
            message.reply_text("❌ Failed to download. Please check the link!")
    else:
        message.reply_text("❌ Invalid TeraBox link! Please send a valid link.")

# Start the Bot
app.run()
