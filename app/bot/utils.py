import inspect
from enum import Enum
from functools import wraps
from typing import Callable, Any, Tuple, List, Optional

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    CallbackContext,
    Application,
    MessageHandler,
    filters,
)
from telegram.ext import ApplicationBuilder, ContextTypes

from app.database import Database
from app.utils import Singleton

from app.startup import DEFAULT_MIN_ACCESS_LEVEL, MAINTENANCE_MODE
from app.constants.defaults import DEFAULT_ACCESS_LEVEL
from app.constants import AccessLevel, DatabaseKeys
from app.constants.strings import (
    MSG_STATE_MAINTENANCE,
    MSG_ERROR_UNKNOWN,
    MSG_NEED_HIGHER_ACCESS_LEVEL,
    MSG_ERROR_EXPECTED_ARGS,
    MSG_ERROR_EXPECTED_AT_LEAST_ARGS,
)

from loguru import logger


async def async_independent_call(func, *args, **kwargs) -> Any:
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


def auth_required(min_level=DEFAULT_MIN_ACCESS_LEVEL, verbose=True, **kwargs: dict):
    """
    Decorator for checking if a user is authorized to use a command.

    Args:
        min_level: Minimum access level for calling specified function.
        verbose: Whether to send information about the fact that user needs higher access level.
        kwargs: Keyword arguments to pass to the decorator.

    Returns:
        A decorator function.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = Database().get_user_by_update(update).data
            if not user:
                if verbose:
                    await update.message.reply_text(MSG_ERROR_UNKNOWN)
                return

            if MAINTENANCE_MODE:
                if (
                    user.get(DatabaseKeys.User.ACCESS_LEVEL, DEFAULT_ACCESS_LEVEL)
                    < AccessLevel.ADMIN
                ):
                    await update.message.reply_text(MSG_STATE_MAINTENANCE)
                    return

            if (
                user.get(DatabaseKeys.User.ACCESS_LEVEL, DEFAULT_ACCESS_LEVEL)
                < min_level
            ):
                if verbose:
                    await update.message.reply_text(MSG_NEED_HIGHER_ACCESS_LEVEL)
                return

            await async_independent_call(func, update, context)

        return wrapper

    return decorator


def args_required(min_arguments=None, exact_arguments=None, error_message=None):
    """
    Decorator for ensuring if function arguments match defined conditions or not.

    Args:
        min_arguments: Minimum required arguments count.
        exact_arguments: Exact arguments count will override min_arguments if set to anything else than 0.
        error_message: Error message that will be shown when arguments count comparison encounters a failure.

    Returns:
        A decorator function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
            query = update.callback_query
            if query:
                await query.answer()
                callback_args = query.data.split(":")
                if (
                    exact_arguments is not None
                    and len(callback_args) != exact_arguments
                ):
                    await query.edit_message_text(
                        error_message or MSG_ERROR_EXPECTED_ARGS.format(exact_arguments)
                    )
                    return
                if min_arguments is not None and len(callback_args) < min_arguments:
                    await query.edit_message_text(
                        error_message
                        or MSG_ERROR_EXPECTED_AT_LEAST_ARGS.format(min_arguments)
                    )
                    return
                return await func(update, context, *callback_args, **kwargs)
            else:
                if exact_arguments is not None and len(args) != exact_arguments:
                    raise ValueError(
                        error_message or MSG_ERROR_EXPECTED_ARGS.format(exact_arguments)
                    )
                if min_arguments is not None and len(args) < min_arguments:
                    raise ValueError(
                        error_message
                        or MSG_ERROR_EXPECTED_AT_LEAST_ARGS.format(min_arguments)
                    )
                return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator


class HandlerType(Enum):
    """
    Enum for handler types.
    """

    COMMAND = 1
    TEXT = 2
    CALLBACK = 3
    ERROR = 4
    UNKNOWN = 5


class BotWrapper(Singleton):
    """
    Wrapper around telegram.ext.ApplicationBuilder for easier bot creation.

    Attributes:
        application: Application instance.
    """

    application: Application = None

    def __init__(self, token: str = None):
        if token and not self.application:
            self.application = ApplicationBuilder().token(token).build()
            self.handlers: List[Tuple[HandlerType, Optional[str], Callable]] = []

    def handler_for(self, command: str):
        """
        Decorator for registering handlers in a container.

        Args:
            command: Command to register handler for.

        Returns:
            A decorator function.
        """

        def decorator(func):
            self.handlers.append(
                (
                    HandlerType.COMMAND,
                    command,
                    func,
                )
            )

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result

            return wrapper

        return decorator

    def text_handler(self):
        """
        Decorator for registering message handlers in a container.

        Returns:
            A decorator function.
        """

        def decorator(func):
            self.handlers.append(
                (
                    HandlerType.TEXT,
                    None,
                    func,
                )
            )

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result

            return wrapper

        return decorator

    def callback_for(self, pattern: str):
        """
        Decorator for registering callback handlers in a container.

        Args:
            pattern: Command to register callback handler for.

        Returns:
            A decorator function.
        """

        def decorator(func):
            self.handlers.append(
                (
                    HandlerType.CALLBACK,
                    pattern,
                    func,
                )
            )

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result

            return wrapper

        return decorator

    def unknown_command_handler(self):
        """
        Decorator for registering unknown command handler in a container.

        Returns:
            A decorator function.
        """

        def decorator(func):
            self.handlers.append(
                (
                    HandlerType.UNKNOWN,
                    None,
                    func,
                )
            )

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result

            return wrapper

        return decorator

    def error_handler(self):
        """
        Decorator for registering error handler in a container.

        Returns:
            A decorator function.
        """

        def decorator(func):
            self.handlers.append(
                (
                    HandlerType.ERROR,
                    None,
                    func,
                )
            )

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result

            return wrapper

        return decorator

    def run(self):
        """
        Infinitely blocking method for running bot in polling mode.

        Before running, all handlers are registered in application by iterating over a `handlers` container
        and matching their type with corresponding telegram.ext.Handler class and telegram.ext.Application
        method for registering handler.
        """

        for handler_type, context, handler in self.handlers:
            match handler_type:
                case HandlerType.COMMAND:
                    self.application.add_handler(CommandHandler(context, handler))
                case HandlerType.TEXT:
                    self.application.add_handler(
                        MessageHandler(filters.TEXT & ~filters.COMMAND, handler)
                    )
                case HandlerType.CALLBACK:
                    self.application.add_handler(
                        CallbackQueryHandler(handler, pattern=context)
                    )
                case HandlerType.ERROR:
                    self.application.add_error_handler(handler)
                case HandlerType.UNKNOWN:
                    self.application.add_handler(
                        MessageHandler(filters.COMMAND, handler)
                    )
                case _:
                    logger.error(
                        f'Unknown type "{handler_type}" for handler "{handler}" with context "{context}"'
                    )

            logger.debug(f"Registered {handler_type}:{handler.__name__}")

        logger.debug(f"Registered handlers: {len(self.application.handlers[0])}")

        self.application.run_polling()


# Monkey patching for running bot like native telegram.ext.Application
BotWrapper.run_polling = BotWrapper.run
