from telegram import Update
from app.constants import AccessLevel, DatabaseKeys
from app.constants.defaults import DEFAULT_NEW_USER
from app.startup import ADMIN_USER_ID
from loguru import logger


def gather_user_data(update: Update) -> dict:
    """Create a user from a Telegram Update."""
    try:
        user_id = update.effective_user.id
        if user_id == ADMIN_USER_ID:
            user_data = {**update.effective_user.to_dict(), **DEFAULT_NEW_USER}
            user_data[DatabaseKeys.User.ACCESS_LEVEL] = AccessLevel.ADMIN
        else:
            user_data = {**update.effective_user.to_dict(), **DEFAULT_NEW_USER}
        return user_id, user_data
    except Exception as e:
        logger.error(f"Error gathering user data: {e}")
        return None, None
