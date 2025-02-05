import time
time.sleep(5)  # Pausa antes de iniciar para evitar desincronización
import os
import logging
import asyncio
from pyrogram import Client, filters
import requests
from aiohttp import web

# Configuración del bot
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIN_CHANNEL = int(os.getenv("BIN_CHANNEL"))
BLOGGER_API_KEY = os.getenv("BLOGGER_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")
FQDN = os.getenv("FQDN")
PORT = int(os.getenv("PORT", 8080))

logging.basicConfig(level=logging.INFO)

# Inicializar el bot
bot = Client("TelegramFileBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

file_storage = {}

@bot.on_message(filters.video | filters.document | filters.audio | filters.photo)
async def handle_files(client, message):
    file = message.video or message.document or message.audio or message.photo
    file_id = file.file_id
    file_name = getattr(file, "file_name", "Unknown")
    file_size = file.file_size
    logging.info(f"Recibido archivo: {file_name} ({file_size} bytes)")

    # Guardar en memoria
    file_storage[file_id] = {"file_name": file_name, "file_size": file_size}

    # Generar enlace de streaming
    stream_url = f"https://{FQDN}/stream/{file_id}"
    
    # Publicar en Blogger
    blogger_url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?key={BLOGGER_API_KEY}"
    post_data = {
        "title": file_name,
        "content": f"Archivo disponible en: <a href='{stream_url}'>Ver aquí</a>",
        "labels": ["Telegram", "Streaming"]
    }
    response = requests.post(blogger_url, json=post_data)
    blog_post = response.json()
    blog_link = blog_post.get("url", "No disponible")
    
    # Enviar confirmación al usuario
    await message.reply_text(f"Tu archivo está disponible aquí: {blog_link}")
    logging.info(f"Publicado en Blogger: {blog_link}")

# Servidor web para streaming
async def stream_handler(request):
    file_id = request.match_info.get("file_id")
    file_data = file_storage.get(file_id)
    if not file_data:
        return web.Response(text="Archivo no encontrado", status=404)
    return web.Response(text=f"Simulación de streaming para {file_data['file_name']}")

app = web.Application()
app.router.add_get("/stream/{file_id}", stream_handler)

async def run_web():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Servidor web iniciado en el puerto {PORT}")

async def main():
    await asyncio.gather(bot.start(), run_web())

if __name__ == "__main__":
    asyncio.run(main())
