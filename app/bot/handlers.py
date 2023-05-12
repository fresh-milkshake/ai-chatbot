from telegram import Update
from telegram.ext import CallbackContext

from app.bot.utils import BotWrapper

from app.startup import TELEGRAM_TOKEN

bot = BotWrapper(TELEGRAM_TOKEN)


@bot.handler_for('start')
async def start(update: Update, context: CallbackContext):
    """
    Handler for /start command.

    Args:
        update: Telegram update.
        context: Telegram context.
    """
    await update.message.reply_text("Hello, world!")


@bot.handler_for('help')
async def help(update: Update, context: CallbackContext):
    """
    Handler for /help command.

    Args:
        update: Telegram update.
        context: Telegram context.
    """
    await update.message.reply_text("Help is not available yet.")
