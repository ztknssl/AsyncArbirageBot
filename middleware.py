from functools import wraps
from json import JSONDecodeError
from typing import Callable, Awaitable, TypeVar, Optional, Any
import aiohttp
from logger import logger

T = TypeVar('T')

""" Декоратор для отлова исключений в асинхронных функциях """
def async_error_catcher(function: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[Optional[T]]]:
    msg = f'An error occurred in: {function.__name__}'

    @wraps(function)
    async def async_func(*args, **kwargs) -> Optional[T]:
        try:
            return await function(*args, **kwargs)
        except aiohttp.ClientError as err:
            logger.error(f"{msg}\nRequest error: {err}", exc_info=True)
        except aiohttp.ContentTypeError as err:
            logger.error(f"{msg}\nInvalid JSON response: {err}", exc_info=True)
        except Exception as err:
            logger.error(f"{msg}\nOther error: {err}", exc_info=True)
        return None

    return async_func

""" Декоратор для отлова исключений в синхронных функциях """
def error_catcher(function: Callable) -> T | None:
    msg = f'An error occurred in: {function.__name__}'

    @wraps(function)
    def sync_func(*args, **kwargs) -> T | None:
        try:
            return function(*args, **kwargs)
        except PermissionError as err:
            logger.error(f'{msg}\nPermission denied: {err}', exc_info=True)
        except JSONDecodeError as err:
            logger.error(f'{msg}\nJSON encoding error: {err}', exc_info=True)
        except Exception as err:
            logger.error(f"{msg}\nError: {err}", exc_info=True)
        return None

    return sync_func