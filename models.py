import aiohttp
import asyncio
from typing import Optional, TypeVar, List, Dict, Tuple
from logger import logger
from config import *
from operator import itemgetter
from abc import ABC, abstractmethod

""" Список сущностей бирж """
EXCHANGES_LIST = []

T = TypeVar('T')

class Exchange(ABC):
    """ Класс представляет собой интерфейс для каждой биржи. При инициализации каждой биржи, её объект сразу будет
        назван по её классу и помещён в список EXCHANGES_LIST. У каждого объекта биржи создается словарь с названием
        тикера и значением в виде списка [бид, аск]. Класс абстрактный, чтобы нельзя было создать экземпляр, а только
        лишь экзепляр класса-наследника в виде конкретной реализованной биржи. Также создается сессия
    """
    def __init__(self):
        self.__name = self.__class__.__name__
        self.coins = {}
        self.__session: Optional[aiohttp.ClientSession] = None
        EXCHANGES_LIST.append(self)

    async def __aenter__(self):
        self.__session = aiohttp.ClientSession()
        return self

    @property
    def name(self):
        return self.__name

    async def __aexit__(self, exc_type, exc, tb):
        if self.__session:
            if not self.__session.closed:
                await self.__session.close()
            self.session = None

    """ Метод get_prices получает данные с биржи и обновляет значение поля coins """
    @abstractmethod
    async def get_prices(self, retries: int = 3, delay: int = 1) -> Dict[str, List[str]]:
        pass

class OKX(Exchange):
    async def __aenter__(self):
        self.__session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.__session:
            if not self.__session.closed:
                await self.__session.close()
            self.session = None

    async def get_prices(self, retries: int=3, delay: int=1) -> Dict[str, List[str]]:

        for attempt in range(retries):
            try:
                async with self.__session.get(url=OKX_URL) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if "data" not in data or not data["data"]:
                        return {}

                    for i in range(len(data['data'])):
                        if data['data'][i]['instId'].endswith('USDT'):
                            ask = data['data'][i]['askPx']
                            bid = data['data'][i]['bidPx']
                            self.coins[(data['data'][i]['instId'].replace('-', ''))] = [bid, ask]
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Ошибка при получении данных для {self.name.upper()}: {str(e)}", exc_info=True)
                logger.warning(f"Попытка {attempt + 1} не удалась для {self.name.upper()}, повторяем...")
                await asyncio.sleep(delay)
        return self.coins


class Binance(Exchange):
    async def __aenter__(self):
        self.__session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.__session:
            if not self.__session.closed:
                await self.__session.close()
            self.session = None

    async def get_prices(self, retries: int=3, delay: int=1) -> Dict[str, List[str]]:

        for attempt in range(retries):
            try:
                async with self.__session.get(url=BINANCE_URL) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if not data:
                        return {}

                    for i in range(len(data)):
                        ask = data[i]['askPrice']
                        bid = data[i]['bidPrice']
                        if data[i]['symbol'].endswith('USDT'):
                            self.coins[(data[i]['symbol'])] = [bid, ask]
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Ошибка при получении данных для {self.name.upper()}: {str(e)}", exc_info=True)
                logger.warning(f"Попытка {attempt + 1} не удалась для {self.name.upper()}, повторяем...")
                await asyncio.sleep(delay)
        return self.coins


class Bybit(Exchange):
    async def __aenter__(self):
        self.__session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.__session:
            if not self.__session.closed:
                await self.__session.close()
            self.session = None

    async def get_prices(self, retries: int=3, delay: int=1) -> Dict[str, List[str]]:

        for attempt in range(retries):
            try:
                async with self.__session.get(url=BYBIT_URL) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if 'result' not in data or not data['result']:
                        return {}

                    for i in range(len(data['result']['list'])):
                        ask = data['result']['list'][i]['ask1Price']
                        bid = data['result']['list'][i]['bid1Price']
                        if data['result']['list'][i]['symbol'].endswith('USDT'):
                            self.coins[(data['result']['list'][i]['symbol'])] = [bid, ask]
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Ошибка при получении данных для {self.name.upper()}: {str(e)}", exc_info=True)
                logger.warning(f"Попытка {attempt + 1} не удалась для {self.name.upper()}, повторяем...")
                await asyncio.sleep(delay)
        return self.coins

""" Функция update_coins_dicts принимает список экземпляров бирж, находит список пересечений по тикерам и помещает в
    переменную updated_keys_list, а затем обновляет поле coins для каждоый биржи, чтобы там находились только те монеты
    со значениями цен, которые есть на каждой бирже
"""
#   Вместо генерации словаря использовал itemgetter из модуля operator, так как скорость этой функции критически важна
#   для арбитража. itemgetter быстрее генерации словаря примерно в полтора раза, насколько я понял

async def update_coins_dicts(exchanges: List[Exchange]) -> None:
    updated_keys_list = list(exchanges[0].coins.keys())

    for i in range(1, len(exchanges)):
        updated_keys_list = list(set(updated_keys_list) & set(exchanges[i].coins.keys()))

    for exchange in exchanges:
        d = dict(zip(updated_keys_list, itemgetter(*updated_keys_list)(exchange.coins)))
        exchange.coins = d
    return None




