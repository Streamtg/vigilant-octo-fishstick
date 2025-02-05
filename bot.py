import os
from pyrogram import Client, filters
import motor.motor_asyncio
import logging

# Configuración de variables de entorno
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
BIN_CHANNEL = os.getenv("BIN_CHANNEL")
BLOGGER_API_KEY = os.getenv("BLOGGER_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
FQDN = os.getenv("FQDN")
PORT = int(os.getenv("PORT", 8080))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del cliente Pyrogram dentro de un virtualenv
app = Client(
    "TelegramFileBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Conexión a MongoDB
db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
database = db_client.get_database()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bienvenido al Telegram File Stream Bot")

@app.on_message(filters.all)
async def handle_media(client, message):
    file_id = None
    file_name = None
    
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.video:
        file_id = message.video.file_id
        file_name = "video.mp4"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name
    elif message.photo:
        file_id = message.photo.file_id
        file_name = "image.jpg"
    elif message.voice:
        file_id = message.voice.file_id
        file_name = "voice.ogg"
    elif message.animation:
        file_id = message.animation.file_id
        file_name = "animation.gif"
    elif message.sticker:
        file_id = message.sticker.file_id
        file_name = "sticker.webp"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_name = "video_note.mp4"
    elif message.contact:
        file_id = message.contact.phone_number
        file_name = "contact.vcf"
    elif message.location:
        file_id = f"Lat: {message.location.latitude}, Lon: {message.location.longitude}"
        file_name = "location.txt"
    elif message.venue:
        file_id = f"{message.venue.title}, {message.venue.address}"
        file_name = "venue.txt"
    elif message.text:
        file_id = message.text
        file_name = "text.txt"
    else:
        await message.reply_text("Formato de archivo no soportado")
        return
    
    file_link = f"https://{FQDN}/stream/{file_id}"
    await message.reply_text(f"Tu archivo está disponible aquí: {file_link}")
    
    # Guardar en MongoDB
    await database.files.insert_one({
        "file_id": file_id,
        "file_name": file_name,
        "url": file_link
    })

if __name__ == "__main__":
    app.run()
