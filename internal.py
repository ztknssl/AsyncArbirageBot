from typing import List
from models import Exchange
from logger import logger
from decimal import Decimal
from middleware import *

""" Функция arbitrage принимает список бирж, желаемый спред с комиссию биржи (для простоты взял единую для всех бирж и
    видов сделок). 
"""

@async_error_catcher
async def arbitrage(exchanges: List[Exchange], spread: Decimal=1, tax_fee: Decimal=0.1) -> None:
    tickers = list(exchanges[0].coins.keys())

    for ticker in tickers:
        # Получаем название монеты
        coin = ticker.replace('USDT', '')

        # Списки бидов и асков для каждой монеты с названиями биржи во втором внутреннем списке, расположенных по индексу
        bids = [[], []]
        asks = [[], []]

        for exchange in exchanges:
            bids[0].append(Decimal(exchange.coins[ticker][0]))
            bids[1].append(exchange.name.upper())
            asks[0].append(Decimal(exchange.coins[ticker][1]))
            asks[1].append(exchange.name.upper())

        if min(asks[0]) != 0:
            if (max(bids[0]) * Decimal((100 + tax_fee) / 100)) / (min(asks[0]) * Decimal((100 + tax_fee) / 100)) > Decimal(1 + spread / 100):

                # Получаем название биржи по индексу максимальной и минимальной цены из второго списка
                max_bids_exchange = bids[1][(bids[0].index(max(bids[0])))]
                min_asks_exchange = asks[1][(asks[0].index(min(asks[0])))]

                await display_info(coin=coin, buy_exchange=min_asks_exchange, sell_exchange=max_bids_exchange,
                                   bid=max(bids[0]), ask=min(asks[0]), spread=spread)



""" Функция display_info считает для условных 100к количество покупаемых монет и профит от продажи с учетом комиссии.
    Выводит результат в консоль и лог-файл
"""

@async_error_catcher
async def display_info(coin: str, buy_exchange: str, sell_exchange: str, bid: Decimal, ask: Decimal, spread: Decimal) -> None:
    total = Decimal(100000)
    quantity = 0

    if bid != 0:
        quantity = total * Decimal((100 - spread) / 100) / bid
    profit = round((quantity * bid) - (quantity * ask) * Decimal((100 - spread) / 100))


    logger.info(f'Нашел спред на монете {coin} между {sell_exchange} и {buy_exchange}')
    logger.info(f'Покупка на бирже {buy_exchange} по цене {ask}')
    logger.info(f'Продажа на бирже {sell_exchange} по цене {bid}')
    logger.info(f'Профит: {profit} $')
    logger.info('----------------------------------------')

