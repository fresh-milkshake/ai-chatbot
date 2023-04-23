import inspect
from functools import wraps
from typing import Callable, List, Any

from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from app.model import LanguageModel
from app.redis import RedisCache
from config import *
from utils.strings import *


async def independent_call(func, *args, **kwargs) -> Any:
    """
    Wrapper around logic of running function async-/synchronously depending
    on target function type - telegram handler or business logic.

    Args:
        func: Target function to call in async or sync mode depending on its type.
        *args: *args that will be provided to target function.
        **kwargs: **kwargs that will be provided to target function.

    Returns:
        Result of target function.
    """

    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


def auth_required(min_level=AccessLevel.GUEST, verbose=True, **kwargs: dict):
    """
    Decorator for checking if a user is authorized to use a command.

    Args:
        min_level: Minimum access level for calling specified function.
        verbose: Whether to send information about fact that user needs higher access level.
        kwargs: Keyword arguments to pass to the decorator.

    Returns:
        A decorator function.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update, context):
            user = RedisCache().get_user_by_update(update)
            if not user:
                if verbose:
                    await update.message.reply_text(MSG_ERROR_UNKNOWN)
                return

            if MAINTENANCE_MODE:
                if user.get(REDIS_USER_ACCESS_LEVEL_KEY, DEFAULT_ACCESS_LEVEL) < AccessLevel.ADMIN:
                    await update.message.reply_text(MSG_STATE_MAINTENANCE)
                    return

            if user.get(REDIS_USER_ACCESS_LEVEL_KEY, DEFAULT_ACCESS_LEVEL) < min_level:
                if verbose:
                    await update.message.reply_text(MSG_NEED_HIGHER_ACCESS_LEVEL)
                return

            await independent_call(func, update, context)

        return wrapper

    return decorator


def args_required(min_arguments=None, exact_arguments=None, error_message=None, is_callback=False):
    """
    Decorator for ensuring if function arguments will match defined conditions or not.

    Args:
        min_arguments: Minimum required arguments count.
        exact_arguments: Exact arguments count, will override min_arguments if set to anything else than 0.
        error_message: Error message that will be shown when arguments count comparison encounters a failure.
        is_callback: Flag that indicated whether function is callback handler or handler of other type.

    Returns:
        A decorator function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if is_callback:
                return

            query = update.callback_query
            await query.answer()

            args = query.data.split(CALLBACK_ARGUMENTS_DIVIDER)
            args_count = len(args)
            args_to_provide = (func, update, context, args, query)

            if exact_arguments and args_count == exact_arguments:
                await independent_call(args_to_provide)
                return

            if min_arguments and args_count >= min_arguments:
                await independent_call(args_to_provide)
                return

            await query.edit_message_text(error_message or MSG_ERROR_INCORRECT_ARGUMENTS)

        return wrapper

    return decorator


@auth_required()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.
    """

    logger.debug(f'User {get_user_string(update)} used /start command')

    await update.message.reply_text(MSG_START)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle unknown commands.
    """

    logger.debug(f'User {get_user_string(update)} used unknown command')

    await update.message.reply_text(MSG_UNKNOWN_COMMAND)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Log errors caused by updates.
    """

    logger.error(f'{update} ---> {context.error}')


@auth_required(min_level=AccessLevel.ADMIN)
async def dump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Dumps all user conversations to disk.
    """

    logger.debug(f'User {get_user_string(update)} used /dump command')

    # RedisCache().get_users()

    raise NotImplementedError


@auth_required(min_level=AccessLevel.USER)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text messages and use the OpenAI API to generate a response.
    """

    logger.info(
        f'Received message from {get_user_string(update)}: {update.message.text}'
    )

    placeholder_message = await update.message.reply_text(
        MSG_WAITING_FOR_RESPONSE)

    user = RedisCache().get_user_by_update(update)

    message_text = update.message.text
    answer = await LanguageModel().create_answer(message_text, user)

    await placeholder_message.delete()

    try:
        await update.message.reply_markdown(answer)
    except Exception as e:
        logger.warning(f'Error while parsing markdown: {e}')
        await update.message.reply_text(answer)


@auth_required(min_level=AccessLevel.ADMIN)
async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /users command.
    """

    logger.debug(f'User {get_user_string(update)} used /users command')

    users = RedisCache().get_users()

    if not users:
        await update.message.reply_text(MSG_NO_USERS)
        return

    users = [
        f"{user.get('first_name')} {user.get('last_name') if user.get('last_name') else '---'} \"{user.get('username')}\" (ID{user.get('id')})"
        for user in users.values()
    ]
    users = '\n'.join(users)

    await update.message.reply_text(users)


@auth_required(min_level=AccessLevel.ADMIN)
async def get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /user command.
    """

    logger.debug(f'User {get_user_string(update)} used /user command')

    if not context.args:
        await update.message.reply_text(MSG_NO_USER_ID)
        return

    user_id = context.args[0]
    if user_id.startswith('ID'):
        user_id = user_id[2:]

    user = RedisCache().get_user(user_id)

    if not user:
        await update.message.reply_text(MSG_USER_NOT_FOUND)
        return

    conversation = user.get('conversation')

    questions_count = 0
    for message in conversation:
        if message.get('role') == 'user':
            questions_count += 1

    message = [
        f"ID: {user.get('id')}", f"Имя: {user.get('first_name')}",
        f"Фамилия: {user.get('last_name') if user.get('last_name') else '---'}",
        f"Имя пользователя: {user.get('username') if user.get('username') else '---'}",
        f"Уровень доступа: {AccessLevel.get_access_level(locale=user.get(REDIS_USER_LANGUAGE_CODE), access_level=user.get(REDIS_USER_ACCESS_LEVEL_KEY))}",
        f"Количество обращений к боту: {questions_count}"
    ]

    message = '\n'.join(message)

    buttons = [
        [
            InlineKeyboardButton(text='Удалить пользователя',
                                 callback_data=f'delete_user {user_id}')
        ],
        [
            InlineKeyboardButton(
                text='Изменить уровень доступа',
                callback_data=f'change_access_level {user_id}')
        ],
        [
            InlineKeyboardButton(
                text='Переслать обращения',
                callback_data=f'forward_requests {user_id}')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   reply_markup=keyboard)


@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
@args_required(exact_arguments=2, error_message=MSG_NO_USER_ID, is_callback=True)
async def delete_user(update: Update, args: list, query: CallbackQuery):
    """
    Handle the /delete_user command.
    """

    logger.debug(f'User {get_user_string(update)} used /delete_user command')

    user_id = args[1]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    if not RedisCache().delete_user(user_id):
        await query.edit_message_text(MSG_USER_NOT_FOUND)
        return

    await query.edit_message_text(MSG_USER_DELETED)


@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
async def change_access_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /change_access_level command.
    """

    logger.debug(
        f'User {get_user_string(update)} used /change_access_level command')

    query = update.callback_query
    await query.answer()

    args = query.data.split(' ')
    if len(args) != 2:
        await query.edit_message_text(MSG_NO_USER_ID)
        return

    user_id = args[1]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    user = RedisCache().get_user(user_id)

    if not user:
        await query.edit_message_text(MSG_USER_NOT_FOUND)
        return

    buttons = []
    for access_level in AccessLevel.LEVELS:
        buttons.append([
            InlineKeyboardButton(
                text=AccessLevel.get_access_level(access_level, 'ru'),
                callback_data=f'change_access_level_confirm {user_id} {access_level}')
        ])

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(MSG_SELECT_ACCESS_LEVEL,
                                  reply_markup=keyboard)


@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
async def change_access_level_confirm(update: Update,
                                      context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /change_access_level_confirm command.
    """

    logger.debug(
        f'User {get_user_string(update)} used /change_access_level_confirm command'
    )

    query = update.callback_query
    await query.answer()

    args = query.data.split(' ')
    if len(args) != 3:
        await query.edit_message_text(MSG_NO_USER_ID)
        return

    user_id = args[1]
    access_level = args[2]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    user = RedisCache().get_user(user_id)

    if not user:
        await query.edit_message_text(MSG_USER_NOT_FOUND)
        return

    user['access_level'] = int(access_level)
    RedisCache().update_user(user_id, user)

    await query.edit_message_text(MSG_ACCESS_LEVEL_CHANGED)

    context.args = [user_id]
    await get_user(update, context)


@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
async def forward_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /forward_requests command.
    """

    logger.debug(f'User {get_user_string(update)} used /forward_requests command')

    query = update.callback_query
    await query.answer()

    args = query.data.split(' ')
    if len(args) != 2:
        await query.edit_message_text(MSG_NO_USER_ID)
        return

    user_id = args[1]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    user = RedisCache().get_user(user_id)

    if not user:
        await query.edit_message_text(MSG_USER_NOT_FOUND)
        return

    for request in user['conversation']:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=request['content'])

    await query.edit_message_text(MSG_REQUESTS_FORWARDED)


async def help_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send a message when the command /help is issued.
    """

    await update.message.reply_text(MSG_HELP)


@auth_required(min_level=AccessLevel.USER)
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Reset the conversation with the user.
    """

    logger.debug(f'User {get_user_string(update)} used /reset command')

    user = RedisCache().get_user_by_update(update)
    user['conversation'] = []
    RedisCache().update_user(user['id'], user)
    await update.message.reply_text(MSG_RESET)


def get_raw_text_handler() -> MessageHandler:
    """
    Get a message handler for handling raw text.

    Returns:
        A message handler for handling raw text.
    """

    return MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler)


def get_unknown_command_handler() -> MessageHandler:
    """
    Get a message handler for handling unknown commands.

    Returns:
        A message handler for handling unknown commands.
    """

    return MessageHandler(filters.COMMAND, unknown_command)


def get_command_handlers() -> List[CommandHandler]:
    """
    Get a list of command handlers.

    Returns:
        A list of command handlers.
    """

    handlers = [
        CommandHandler('start', start),
        CommandHandler('help', help_info),
        CommandHandler('reset', reset),
        CommandHandler('users', get_users),
        CommandHandler('user', get_user),
        CallbackQueryHandler(get_users, pattern=r'^/users \d+$'),
        CallbackQueryHandler(get_user, pattern=r'^/user \d+$'),
        CallbackQueryHandler(delete_user, pattern=r'^delete_user \d+$'),
        CallbackQueryHandler(change_access_level, pattern=r'^change_access_level \d+$'),
        CallbackQueryHandler(change_access_level_confirm, pattern=r'^change_access_level_confirm \d+ \d+$'),
        CallbackQueryHandler(forward_requests, pattern=r'^forward_requests \d+$'),
        get_raw_text_handler(),
        get_unknown_command_handler(),
    ]

    return handlers
