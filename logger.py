from config import LOGS
from loguru import logger


""" Настройка логгера с асинхронной очередью для вывода в консоль и запись в лог-файл, с ротацией и сжатием """
# Сначала хотел, чтобы логи писались в json-файл, но он получается невалидным. Настройку
# подходящую я не смог найти, а костыль писать не хотелось) Видимо, он только для потоковой обработки
# Напишите, пожалуйста, если такая настройка в loguru есть

logger.add(
    sink=LOGS,
    enqueue=True,
    rotation='1 MB',
    compression='zip',
    format='{time} {level} {message}',
    level='DEBUG',
    catch=True
)