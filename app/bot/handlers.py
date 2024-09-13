import json
import os
import time
from loguru import logger
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

import app.constants.strings as strings
from app.bot.utils import BotWrapper, auth_required, args_required
from app.constants import AccessLevel, DatabaseKeys
from app.constants.defaults import DEFAULT_ACCESS_LEVEL, RATE_LIMIT_PAUSE
from app.constants.models import AvailableModels
from app.constants.paths import TMP_FILE_NAME
from app.database import Database
from app.model import LanguageModel
from app.startup import TELEGRAM_BOT_TOKEN
from app.utils import get_user_string

bot = BotWrapper(TELEGRAM_BOT_TOKEN)


@bot.handler_for("start")
@auth_required()
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.
    """

    logger.debug(f"User {get_user_string(update)} used /start command")

    await update.message.reply_text(strings.MSG_WELCOME)


@bot.unknown_command_handler()
async def unknown_command(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Handle unknown commands.
    """

    logger.debug(f"User {get_user_string(update)} used unknown command")

    await update.message.reply_text(strings.MSG_UNKNOWN_COMMAND)


@bot.error_handler()
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Log errors caused by updates and notify admins.
    """
    error = context.error

    logger.error(f"Update {update} caused error: {error}")

    # check if we have infernet connection with telegram servers and if we have - send message to admins
    try:
        # Check if we have internet connection with Telegram servers
        await context.bot.get_me()
    except Exception as e:
        logger.error(f"Failed to connect to Telegram servers: {e}")
        return

    admin_chat_ids = []
    response = Database().get_users()
    if response.success:
        users = response.data
        for user in users.values():
            if user.get(DatabaseKeys.User.ACCESS_LEVEL) == AccessLevel.ADMIN:
                admin_chat_ids.append(user.get(DatabaseKeys.User.ID))

    try:
        error_message = (
            f"An error occurred:\n\n"
            f"Update ID: {update.update_id}\n"
            f"User: {update.effective_user.first_name} (ID: {update.effective_user.id})\n"
            f"Message: '{update.message.text}'\n"
            f"Date: {update.message.date}\n\n"
            f"Error: {error}"
        )
    except Exception:
        error_message = (
            "An error occurred:\n\n" f"Update\n{str(update)}\n" f"Error\n{error}"
        )

    for admin_id in admin_chat_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=error_message)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


@bot.handler_for("raise_error")
@auth_required(min_level=AccessLevel.ADMIN)
async def raise_error(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Raise an error to test the error handler.
    """
    raise Exception("This is a test error")


@bot.handler_for("dump")
@auth_required(min_level=AccessLevel.ADMIN)
async def dump(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /dump command.
    Dumps all user data into a JSON file and sends it as a document.
    """
    logger.debug(f"User {get_user_string(update)} used /dump command")

    response = Database().get_users()
    if not response.success:
        await update.message.reply_text(strings.MSG_NO_USERS)
        return

    users = response.data

    dump_data = [
        {
            "id": user_id,
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "username": user_data.get("username"),
            "access_level": AccessLevel.from_int(
                locale=user_data.get(DatabaseKeys.User.LANGUAGE_CODE),
                access_level=user_data.get(DatabaseKeys.User.ACCESS_LEVEL),
            ),
            "conversation": user_data.get("conversation"),
        }
        for user_id, user_data in users.items()
    ]

    try:
        with open(TMP_FILE_NAME, "w", encoding="utf-8") as temp_file:
            json.dump(dump_data, temp_file, indent=4, ensure_ascii=False)

        with open(TMP_FILE_NAME, "rb") as file:
            await update.message.reply_document(file, filename=TMP_FILE_NAME)
    except Exception as e:
        logger.error(f"Failed to send user dump: {e}")
        await update.message.reply_text("Failed to generate user dump.")
    finally:
        if os.path.exists(TMP_FILE_NAME):
            os.remove(TMP_FILE_NAME)


@bot.text_handler()
@auth_required(min_level=AccessLevel.USER)
async def text_handler(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Handle text messages and use the Provider to generate a response.
    """

    logger.info(
        f"Received message from {get_user_string(update)}: {update.message.text}"
    )

    response = Database().get_user_by_update(update)

    if not response.success:
        await update.message.reply_text(strings.MSG_USER_NOT_FOUND)
        return

    user = response.data

    placeholder_message = await update.message.reply_text(
        strings.MSG_WAITING_FOR_RESPONSE
    )

    full_response = ""
    last_response = ""
    rate_limit = time.time() + RATE_LIMIT_PAUSE

    async for chunk in LanguageModel().stream_answer(update.message.text, user):
        full_response += chunk

        if full_response.strip() == last_response.strip() or time.time() < rate_limit:
            continue

        rate_limit = time.time() + RATE_LIMIT_PAUSE

        try:
            await placeholder_message.edit_text(full_response)
            last_response = full_response
        except Exception as e:
            logger.error(f"Error while editing message: {e}")

    if not full_response:
        logger.error("Got empty response from model")
    else:
        logger.info(f"Response:\n{full_response}")
        try:
            if full_response != last_response:
                await placeholder_message.edit_text(full_response)
        except Exception as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Error while editing final message: {e}")


@bot.handler_for("users")
@auth_required(min_level=AccessLevel.ADMIN)
async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /users command.
    """

    logger.debug(f"User {get_user_string(update)} used /users command")

    response = Database().get_users()

    if not response.success:
        await update.message.reply_text(strings.MSG_NO_USERS)
        return

    users = response.data

    users = [
        f"{user.get('first_name')} {user.get('last_name', '---')} \"{user.get('username', '')}\" (ID{user.get('id')})"
        for user in users.values()
    ]
    users = "\n".join(users)

    await update.message.reply_text(users)


@bot.handler_for("model")
@auth_required(min_level=AccessLevel.USER)
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /model command.
    """

    logger.debug(f"User {get_user_string(update)} used /model command")

    response = Database().get_user_by_update(update)

    if not response.success:
        await update.message.reply_text(strings.MSG_USER_NOT_FOUND)
        return

    user = response.data

    keyboard = [
        [
            InlineKeyboardButton(
                model.name,
                callback_data=f"choose_model:{model.name}",
            )
        ]
        for model in AvailableModels.filter_by_access_level(
            user.get(DatabaseKeys.User.ACCESS_LEVEL, DEFAULT_ACCESS_LEVEL)
        )
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                strings.BTN_CANCEL,
                callback_data="cancel",
            )
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(strings.MSG_CHOOSE_MODEL, reply_markup=reply_markup)


@bot.callback_for("cancel")
@auth_required(min_level=AccessLevel.USER)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the cancel button.
    """

    logger.debug(f"User {get_user_string(update)} used cancel button")

    await update.callback_query.answer()
    await update.callback_query.message.edit_text(strings.MSG_CANCELLED)


# @bot.handler_for("users")
# @auth_required(min_level=AccessLevel.ADMIN)
# async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Handle the /users command.
#     """

#     logger.debug(f"User {get_user_string(update)} used /users command")

#     response = Database().get_users()

#     if not response.success:
#         await update.message.reply_text(strings.MSG_NO_USERS)
#         return

#     users = response.data

#     users = [
#         f"{user.get('first_name')} {user.get('last_name') if user.get('last_name') else '---'} \"{user.get('username')}\" (ID{user.get('id')})"
#         for user in users.values()
#     ]
#     users = "\n".join(users)

#     await update.message.reply_text(users)


@bot.callback_for("choose_model")
@auth_required(min_level=AccessLevel.USER)
async def choose_model_callback(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /model callback.
    """

    logger.debug(f"User {get_user_string(update)} used /model callback")

    query = update.callback_query
    await query.answer()

    response = Database().get_user_by_update(update)

    if not response.success:
        await query.answer(strings.MSG_USER_NOT_FOUND, show_alert=True)
        return

    user = response.data
    model_name = query.data.split(":")[1]

    chosen_model = next(
        (model for model in AvailableModels.ALL() if model.name == model_name), None
    )

    if chosen_model:
        user[DatabaseKeys.User.CHOSEN_MODEL] = model_name

        response = Database().update_user_by_id(user.get("id"), user)

        if response.success:
            await query.edit_message_text(strings.MSG_MODEL_CHOSEN.format(model_name))
        else:
            await query.edit_message_text(strings.MSG_FAILED_UPDATE_USER)
    else:
        await query.edit_message_text(strings.MSG_MODEL_NOT_FOUND)


@bot.handler_for("state")
@auth_required(min_level=AccessLevel.USER)
async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /state command.
    """

    logger.debug(f"User {get_user_string(update)} used /state command")

    await update.message.reply_text(
        strings.MSG_STATE.format(LanguageModel().stability_percentage())
    )


@bot.handler_for("set_rate_limit_pause")
@auth_required(min_level=AccessLevel.ADMIN)
async def rate_limit_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /rate_limit_pause command.
    """

    logger.debug(f"User {get_user_string(update)} used /rate_limit_pause command")

    if not context.args:
        await update.message.reply_text("Usage: /set_rate_limit_pause <seconds>")
        return

    try:
        rate_limit_pause = int(context.args[0])

        if rate_limit_pause <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(strings.MSG_INVALID_RATE_LIMIT_PAUSE)
        return

    global RATE_LIMIT_PAUSE
    RATE_LIMIT_PAUSE = rate_limit_pause

    await update.message.reply_text(
        strings.MSG_RATE_LIMIT_PAUSE_SET.format(rate_limit_pause)
    )


@bot.handler_for("admin_commands")
@auth_required(min_level=AccessLevel.ADMIN)
async def admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /admin_commands command.
    """

    logger.debug(f"User {get_user_string(update)} used /admin_commands command")

    commands = [
        "/set_rate_limit_pause <seconds>",
        "/user <user_id>",
        "/users",
        "/delete_user <user_id>",
        "/dump",
    ]

    commands = "\n".join(commands)

    await update.message.reply_text(commands)


@bot.handler_for("user")
@auth_required(min_level=AccessLevel.ADMIN)
async def get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /user command.
    """

    logger.debug(f"User {get_user_string(update)} used /user command")

    if not context.args:
        await update.message.reply_text(strings.MSG_NO_USER_ID)
        return

    user_id = context.args[0]
    if user_id.startswith("ID"):
        user_id = user_id[2:]

    response = Database().get_user(user_id)

    if not response.success:
        await update.message.reply_text(strings.MSG_USER_NOT_FOUND)
        return

    user = response.data

    conversation = user.get("conversation")

    questions_count = 0
    for message in conversation:
        if message.get("role") == "user":
            questions_count += 1

    message = [
        f"ID: {user.get('id')}",
        f"Имя: {user.get('first_name')}",
        f"Фамилия: {user.get('last_name') if user.get('last_name') else '---'}",
        f"Имя пользователя: {user.get('username') if user.get('username') else '---'}",
        f"Уровень доступа: {AccessLevel.from_int(locale=user.get(DatabaseKeys.User.LANGUAGE_CODE), access_level=user.get(DatabaseKeys.User.ACCESS_LEVEL))}",
        f"Количество обращений к боту: {questions_count}",
    ]

    message = "\n".join(message)

    buttons = [
        [
            InlineKeyboardButton(
                text="Удалить пользователя", callback_data=f"delete_user {user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить уровень доступа",
                callback_data=f"choose_access_level {user_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Переслать обращения", callback_data=f"forward_requests {user_id}"
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, reply_markup=keyboard
    )


@bot.handler_for("delete_user")
@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
@args_required(exact_arguments=2, error_message=strings.MSG_NO_USER_ID)
async def delete_user(update: Update, args: list, query: CallbackQuery):
    """
    Handle the /delete_user command.
    """

    logger.debug(f"User {get_user_string(update)} used /delete_user command")

    user_id = args[1]

    if user_id.startswith("ID"):
        user_id = int(user_id[2:])

    if not Database().delete_user(user_id).success:
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    await query.edit_message_text(strings.MSG_USER_DELETED)


@bot.callback_for("choose_access_level")
@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
async def choose_access_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /choose_access_level command.
    """

    logger.debug(f"User {get_user_string(update)} used /choose_access_level command")

    query = update.callback_query
    await query.answer()

    args = query.data.split(" ")
    logger.debug(f"Args: {args}")
    if len(args) != 2:
        await query.edit_message_text(strings.MSG_NO_USER_ID)
        return

    user_id = args[1]

    if user_id.startswith("ID"):
        user_id = int(user_id[2:])

    buttons = []

    for access_level in AccessLevel.all():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=AccessLevel.from_int(access_level=access_level, locale="ru"),
                    callback_data=f"change_access_level_confirm {user_id} {access_level}",
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        strings.MSG_SELECT_ACCESS_LEVEL, reply_markup=keyboard
    )


@bot.callback_for("change_access_level_confirm")
@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
async def change_access_level_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Handle the /change_access_level_confirm command.
    """

    logger.debug(
        f"User {get_user_string(update)} used /change_access_level_confirm command"
    )

    query = update.callback_query
    await query.answer()

    args = query.data.split(" ")
    logger.debug(f"Args: {args}")
    if len(args) != 3:
        await query.edit_message_text(strings.MSG_NO_USER_ID)
        return

    user_id = args[1]
    access_level = args[2]

    try:
        user_id = int(user_id)
        access_level = int(access_level)
    except ValueError:
        await query.edit_message_text(strings.MSG_INVALID_INPUT)
        return

    response = Database().get_user(user_id)

    if not response.success:
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    user = response.data

    if access_level not in AccessLevel.all():
        await query.edit_message_text(strings.MSG_INVALID_ACCESS_LEVEL)
        return

    user[DatabaseKeys.User.ACCESS_LEVEL] = access_level
    update_response = Database().update_user_by_id(user_id, user)

    if not update_response.success:
        await query.edit_message_text(strings.MSG_UPDATE_FAILED)
        return

    await query.edit_message_text(strings.MSG_ACCESS_LEVEL_CHANGED)

    context.args = [str(user_id)]
    await get_user(update, context)


@bot.callback_for("forward_requests")
@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
async def forward_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /forward_requests command.
    """

    logger.debug(f"User {get_user_string(update)} used /forward_requests command")

    query = update.callback_query
    await query.answer()

    args = query.data.split(" ")
    if len(args) != 2:
        await query.edit_message_text(strings.MSG_NO_USER_ID)
        return

    user_id = args[1]

    if user_id.startswith("ID"):
        user_id = int(user_id[2:])

    response = Database().get_user(user_id)

    if not response.success:
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    user = response.data

    for request in user["conversation"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=request["content"]
        )

    await query.edit_message_text(strings.MSG_REQUESTS_FORWARDED)


@bot.handler_for("help")
async def help_info(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Send a message when the command /help is issued.
    """

    await update.message.reply_text(strings.MSG_HELP)


@bot.handler_for("reset")
@auth_required(min_level=AccessLevel.USER)
async def reset(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Reset the conversation with the user.
    """

    logger.debug(f"User {get_user_string(update)} used /reset command")

    user = Database().get_user_by_update(update)

    if not user.success:
        await update.message.reply_text(strings.MSG_USER_NOT_FOUND)
        return

    user = user.data

    user["conversation"] = []
    Database().update_user_by_id(user["id"], user)
    await update.message.reply_text(strings.MSG_RESET)
