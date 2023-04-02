from telegram import Update


def get_user_string(update: Update) -> str:
    """
    Get a string representation of a user.

    Args:
        user: A dictionary containing user data.

    Returns:
        A string representation of the user.
    """
    return f"\"{update.effective_user.first_name} {update.effective_user.username}\" (ID{update.effective_user.id})"


def get_id_from_update(update: Update) -> int:
    """
    Get the user ID of a user.

    Args:
        user: A dictionary containing user data.

    Returns:
        The user ID of the user.
    """
    return update.effective_user.id


def get_user_name(update: Update) -> str:
    """
    Get the user name of a user.

    Args:
        user: A dictionary containing user data.

    Returns:
        The user name of the user.
    """
    return update.effective_user.first_name