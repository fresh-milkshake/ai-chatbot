from utils.logging import setup_logger

setup_logger()

import app.bot as bot
from config import PRODUCTION, TELEGRAM_TOKEN
from telegram.ext import ApplicationBuilder, CommandHandler

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

for handler in bot.get_command_handlers():
    application.add_handler(handler)

if PRODUCTION:
    application.add_error_handler(bot.error_handler)