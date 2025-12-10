# handlers/start_handler.py

from telegram import Update
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext):
    # Lógica de /start
    await update.message.reply_text("Bienvenido al bot!")
    