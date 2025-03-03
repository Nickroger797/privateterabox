import os
import asyncio
import requests
import re
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from aiohttp import web

# 🔹 Telegram Bot Credentials
API_ID = int(os.getenv("API_ID"))  
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔹 Initialize Pyrogram Bot
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Function to Extract TeraBox Direct Download Link
def get_terabox_download_link(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all("script")

        for script in script_tags:
            if "download" in script.text:
                match = re.search(r"(https://[^'\"]+download.[^'\"]+)", script.text)
                if match:
                    return match.group(1)
    
    return None

# 🔹 Function to Download File
def download_from_terabox(url):
    download_link = get_terabox_download_link(url)

    if not download_link:
        return None

    file_name = "downloaded_file.zip"
    response = requests.get(download_link, stream=True)

    with open(file_name, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    return file_name

# 🔹 Telegram Command Handlers
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Welcome to TeraBox Downloader Bot!\n\nSend me a TeraBox link to download the file.")

@app.on_message(filters.text)
async def process_link(client, message):
    url = message.text.strip()

    if "terabox.com" in url:
        await message.reply_text("🔍 Processing your link, please wait...")

        file_path = download_from_terabox(url)

        if file_path:
            await message.reply_document(file_path, caption="✅ Here is your downloaded file!")
            os.remove(file_path)
        else:
            await message.reply_text("❌ Failed to download. Please check the link!")
    else:
        await message.reply_text("❌ Invalid TeraBox link! Please send a valid link.")

# 🔹 Web Server for Koyeb Health Check
async def healthcheck(request):
    return web.Response(text="Bot is running")

async def start():
    # Start Pyrogram Bot
    loop.create_task(app.run())

    # Start Web Server (For Koyeb Health Check)
    runner = web.AppRunner(web.Application())
    runner.app.router.add_get("/", healthcheck)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

# 🔹 Start the Bot
if __name__ == "__main__":
    asyncio.run(start())
