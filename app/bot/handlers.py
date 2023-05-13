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
from app.constants import AccessLevel, RedisKeys
from app.constants.defaults import DEFAULT_ACCESS_LEVEL
from app.database import RedisCache
from app.constants.models import AvailableModels
from app.model import ExternalLanguageModel
from app.startup import TELEGRAM_TOKEN
from app.utils import get_user_string


bot = BotWrapper(TELEGRAM_TOKEN)


@bot.handler_for('start')
@auth_required()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.
    """

    logger.debug(f'User {get_user_string(update)} used /start command')

    await update.message.reply_text(strings.MSG_START)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle unknown commands.
    """

    logger.debug(f'User {get_user_string(update)} used unknown command')

    await update.message.reply_text(strings.MSG_UNKNOWN_COMMAND)


@bot.error_handler()
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Log errors caused by updates.
    """

    logger.error(f'{update} ---> {context.error}')


@bot.handler_for('dump')
@auth_required(min_level=AccessLevel.ADMIN)
async def dump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Dumps all user conversations to disk.
    """

    logger.debug(f'User {get_user_string(update)} used /dump command')

    # RedisCache().get_users()

    raise NotImplementedError


@bot.text_handler()
@auth_required(min_level=AccessLevel.USER)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text messages and use the OpenAI API to generate a response.
    """

    logger.info(
        f'Received message from {get_user_string(update)}: {update.message.text}'
    )

    placeholder_message = await update.message.reply_text(
        strings.MSG_WAITING_FOR_RESPONSE)

    user = RedisCache().get_user_by_update(update)

    message_text = update.message.text
    answer = await ExternalLanguageModel().create_answer(message_text, user)

    await placeholder_message.delete()

    try:
        await update.message.reply_markdown(answer)
    except Exception as e:
        logger.warning(f'Error while parsing markdown: {e}')
        await update.message.reply_text(answer)


@bot.handler_for('users')
@auth_required(min_level=AccessLevel.ADMIN)
async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /users command.
    """

    logger.debug(f'User {get_user_string(update)} used /users command')

    users = RedisCache().get_users()

    if not users:
        await update.message.reply_text(strings.MSG_NO_USERS)
        return

    users = [
        f"{user.get('first_name')} {user.get('last_name') if user.get('last_name') else '---'} \"{user.get('username')}\" (ID{user.get('id')})"
        for user in users.values()
    ]
    users = '\n'.join(users)

    await update.message.reply_text(users)


@bot.handler_for('model')
@auth_required(min_level=AccessLevel.USER)
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /model command.
    """

    logger.debug(f'User {get_user_string(update)} used /model command')

    user = RedisCache().get_user_by_update(update)

    keyboard = []
    for model in AvailableModels.ALL:
        if user.get(RedisKeys.User.ACCESS_LEVEL, DEFAULT_ACCESS_LEVEL) >= model.min_access_level:
            keyboard.append([InlineKeyboardButton(model.name, callback_data=f'choose_model:{model.name}')])

    keyboard = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(strings.MSG_CHOOSE_MODEL, reply_markup=keyboard)


@bot.callback_for('choose_model')  # TODO: i dont sure if this is right callback pattern
@auth_required(min_level=AccessLevel.USER)
async def choose_model_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /model callback.
    """

    logger.debug(f'User {get_user_string(update)} used /model callback')

    user = RedisCache().get_user_by_update(update)

    model_name = update.callback_query.data.split(':')[1]

    for model in AvailableModels.ALL:
        if model.name == model_name:
            user[RedisKeys.User.LOCAL_MODEL] = model_name
            RedisCache().update_user(
                user.get('id'), user
            )
            break

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(strings.MSG_MODEL_CHOSEN.format(model_name))


@bot.handler_for('state')
@auth_required(min_level=AccessLevel.USER)
async def state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /state command.
    """

    logger.debug(f'User {get_user_string(update)} used /state command')

    await update.message.reply_text(strings.MSG_STATE.format(ExternalLanguageModel().stability_percentage))


@bot.handler_for('user')
@auth_required(min_level=AccessLevel.ADMIN)
async def get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /user command.
    """

    logger.debug(f'User {get_user_string(update)} used /user command')

    if not context.args:
        await update.message.reply_text(strings.MSG_NO_USER_ID)
        return

    user_id = context.args[0]
    if user_id.startswith('ID'):
        user_id = user_id[2:]

    user = RedisCache().get_user(user_id)

    if not user:
        await update.message.reply_text(strings.MSG_USER_NOT_FOUND)
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
        f"Уровень доступа: {AccessLevel.from_int(locale=user.get(RedisKeys.User.LANGUAGE_CODE), access_level=user.get(RedisKeys.User.ACCESS_LEVEL))}",
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


@bot.handler_for('delete_user')
@auth_required(min_level=AccessLevel.ADMIN, verbose=False)
@args_required(exact_arguments=2, error_message=strings.MSG_NO_USER_ID)
async def delete_user(update: Update, args: list, query: CallbackQuery):
    """
    Handle the /delete_user command.
    """

    logger.debug(f'User {get_user_string(update)} used /delete_user command')

    user_id = args[1]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    if not RedisCache().delete_user(user_id):
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    await query.edit_message_text(strings.MSG_USER_DELETED)


@bot.callback_for('change_access_level')  # TODO: same as in callback handler above
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
        await query.edit_message_text(strings.MSG_NO_USER_ID)
        return

    user_id = args[1]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    user = RedisCache().get_user(user_id)

    if not user:
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    buttons = []
    for access_level in AccessLevel().all:
        buttons.append([
            InlineKeyboardButton(
                text=AccessLevel.from_int(access_level, 'ru'),
                callback_data=f'change_access_level_confirm {user_id} {access_level}')
        ])

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(strings.MSG_SELECT_ACCESS_LEVEL,
                                  reply_markup=keyboard)


@bot.callback_for('change_access_level_confirm')
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
        await query.edit_message_text(strings.MSG_NO_USER_ID)
        return

    user_id = args[1]
    access_level = args[2]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    user = RedisCache().get_user(user_id)

    if not user:
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    user['access_level'] = int(access_level)
    RedisCache().update_user(user_id, user)

    await query.edit_message_text(strings.MSG_ACCESS_LEVEL_CHANGED)

    context.args = [user_id]
    await get_user(update, context)


@bot.callback_for('forward_requests')
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
        await query.edit_message_text(strings.MSG_NO_USER_ID)
        return

    user_id = args[1]

    if user_id.startswith('ID'):
        user_id = int(user_id[2:])

    user = RedisCache().get_user(user_id)

    if not user:
        await query.edit_message_text(strings.MSG_USER_NOT_FOUND)
        return

    for request in user['conversation']:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=request['content'])

    await query.edit_message_text(strings.MSG_REQUESTS_FORWARDED)


@bot.handler_for('help')
async def help_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send a message when the command /help is issued.
    """

    await update.message.reply_text(strings.MSG_HELP)


@bot.handler_for('reset')
@auth_required(min_level=AccessLevel.USER)
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Reset the conversation with the user.
    """

    logger.debug(f'User {get_user_string(update)} used /reset command')

    user = RedisCache().get_user_by_update(update)
    user['conversation'] = []
    RedisCache().update_user(user['id'], user)
    await update.message.reply_text(strings.MSG_RESET)
