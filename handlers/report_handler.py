# handlers/report_handler.py

from telegram import Update
from telegram.ext import CallbackContext

async def report(update: Update, context: CallbackContext):
    # Lógica de /report
    await update.message.reply_text("Por favor selecciona una categoría.")
    