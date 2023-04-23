from utils.logging import setup_logger

setup_logger()

import app.bot as bot
from config import MAINTENANCE_MODE, TELEGRAM_TOKEN
from telegram.ext import ApplicationBuilder
from loguru import logger

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

for handler in bot.get_command_handlers():
    application.add_handler(handler)

if MAINTENANCE_MODE == 'True':
    logger.info('Maintenance mode is enabled')
    application.add_error_handler(bot.error_handler)
