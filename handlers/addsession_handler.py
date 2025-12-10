# handlers/addsession_handler.py

from telegram import Update
from telegram.ext import CallbackContext

async def addsession(update: Update, context: CallbackContext):
    # Lógica para agregar una sesión
    await update.message.reply_text("Agregando sesión...")
    