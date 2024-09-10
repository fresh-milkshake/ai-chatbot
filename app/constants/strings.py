# Grouping the string constants

# Text literals for bot messages
MSG_WELCOME = (
    "Привет! Я бот работающий с разными ИИ провайдерами. Чтобы узнать, что я умею, напиши /help.\n"
    'Чтобы начать общение, просто напиши мне что-нибудь, или задай вопрос, например "Что такое GPT-3?"'
)
MSG_HELP = (
    "Я - ИИ бот. Я могу помочь с ответами на вопросы, генерировать тексты, исправлять ошибки и многое другое.\n"
    'Ты можешь начать общение со мной, написав что-нибудь, например "Идея для вкусного и полезного завтрака".\n'
    "Доступные команды:\n"
    "/help - провторно вывести это сообщение.\n"
    "/start - приветственное сообщение.\n"
    "/reset - сбросить текущий диалог. Удаляет его историю, и можно начать новый, на другую тему.\n"
    "/model - изменить модель.\n"
    "/state - проверить состояние бота.\n"
)

# Unknown command error messages
MSG_UNKNOWN_COMMAND = "Неизвестная команда. Чтобы узнать, что я умею, напиши /help."

# Error messages
MSG_ERROR_UNKNOWN = "Произошла неизвестная ошибка. Перезапустите бота и попробуйте снова или подождите некоторое время."
MSG_ERROR_NO_API_KEY = "Не указан API-ключ OpenAI. Пожалуйста, укажите его в переменной окружения OPENAI_API_KEY."
MSG_ERROR_MODEL_INVALID_REQUEST_ERROR = (
    "Произошла ошибка при формировании запроса. Похоже, что размер диалога "
    "превышает максимально допустимый размер, впоспользуйтесь командой /reset "
    "для сброса диалога."
)
MSG_ERROR_MODEL_API_ERROR = (
    "Произошла ошибка при обращении к API. Пожалуйста, попробуйте снова или подождите "
    "некоторое время."
)
MSG_ERROR_MODEL_OPENAI_ERROR = (
    "Произошла ошибка на стороне внешнего API, возможно, проблемы с соединением. "
    "Пожалуйста, попробуйте снова или подождите некоторое время."
)

MSG_ERROR_EXPECTED_ARGS = "Ожидалось {} аргументов"
MSG_ERROR_EXPECTED_AT_LEAST_ARGS = "Ожидалось не менее {} аргументов"

# Bot state messages
MSG_STATE_ONLINE = "✅ Бот в сети и исправно работает"
MSG_STATE_OPENAI_ERRORS = "⚠️ Бот в сети, но возможны ошибки"
MSG_STATE_MAINTENANCE = "🔧 Проходит обслуживание бота, подождите некоторое время"
MSG_STATE_RESTARTING = "🔄️ Бот перезапускается, подождите некоторое время"

# Access level messages
MSG_NEED_HIGHER_ACCESS_LEVEL = "Недостаточно прав."
MSG_SELECT_ACCESS_LEVEL = "Выберите уровень доступа:"
MSG_ACCESS_LEVEL_CHANGED = "Уровень доступа успешно изменен."

# Reset dialog messages
MSG_RESET = "Диалог успешно сброшен."
MSG_WAITING_FOR_RESPONSE = "Подождите, я думаю..."

# User management messages
MSG_USERS = "Пользователи:"
MSG_USER_NOT_FOUND = "Пользователь не найден."
MSG_NO_USERS = "Нет пользователей."
MSG_NO_USER_ID = "Не указан ID пользователя."
MSG_USER_DELETED = "Пользователь успешно удален."
MSG_REQUESTS_FORWARDED = "Запросы успешно перенаправлены."

# Model-related messages
MSG_CHOOSE_MODEL = "Выберите модель для генерации текста:"
MSG_MODEL_CHOSEN = "Выбрана модель: {0}"

# Error messages for incorrect arguments
MSG_ERROR_INCORRECT_ARGUMENTS = "Неправильное количество аргументов"

# Report messages
MSG_REPORT_CREATED = "Отчет о диалогах успешно создан. Записано байт: {}\nСписок новых/измененных файлов:\n{}"

# Bot state message
MSG_STATE = "Стабильность работы в данный момент: {0:.2f}%"

BTN_CANCEL = "Отмена"
MSG_CANCELLED = "Операция отменена."


MSG_INVALID_RATE_LIMIT_PAUSE = (
    "Неверный формат аргумента. Используйте целое положительное число."
)
MSG_RATE_LIMIT_PAUSE_SET = "Задержка ограничения скорости установлена на {0} секунд."
MSG_NOT_ENOUGH_ARGUMENTS = "Недостаточно аргументов."
MSG_FAILED_UPDATE_USER = "Не удалось обновить данные пользователя"
MSG_MODEL_NOT_FOUND = "Не удалось найти модель"

MSG_INVALID_ACCESS_LEVEL = (
    "Неверный формат аргумента. Используйте целое положительное число."
)
MSG_UPDATE_FAILED = "Не удалось обновить данные пользователя"
MSG_INVALID_INPUT = "Неверный формат аргумента. Используйте целое положительное число."
