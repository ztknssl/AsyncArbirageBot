from typing import List
from models import Exchange
from logger import logger
from decimal import Decimal


""" Функция arbitrage принимает список бирж, желаемый спред с комиссию биржи (для простоты взял единую для всех бирж и
    видов сделок). 
"""
async def arbitrage(exchanges: List[Exchange], spread: Decimal=1, tax_fee: Decimal=0.1) -> None:
    tickers = list(exchanges[0].coins.keys())

    for ticker in tickers:
        # Получаем название монеты
        coin = ticker.replace('USDT', '')

        # Списки бидов и асков для каждой монеты
        bids = []
        asks = []

        for exchange in exchanges:
            bids.append(Decimal(exchange.coins[ticker][0]))
            asks.append(Decimal(exchange.coins[ticker][1]))

        try:
            if min(asks) != 0:
                if (max(bids) * Decimal((100 + tax_fee) / 100)) / (min(asks) * Decimal((100 + tax_fee) / 100)) > Decimal(1 + spread / 100):
                    max_bids_exchange = ''
                    min_asks_exchange = ''

                    # Получаем название биржи из той подходящей цены, которую нашли, путём сравнения
                    for exchange in exchanges:
                        if max(bids) == Decimal(exchange.coins[ticker][0]):
                            max_bids_exchange = exchange.name.upper()
                        if min(asks) == Decimal(exchange.coins[ticker][1]):
                            min_asks_exchange = exchange.name.upper()

                    await display_info(coin=coin, buy_exchange=min_asks_exchange, sell_exchange=max_bids_exchange,
                                       bid=max(bids), ask=min(asks), spread=spread)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка в функции arbitrage: {str(e)}", exc_info=True)


""" Функция display_info считает для условных 100к количество покупаемых монет и профит от продажи с учетом комиссии.
    Выводит результат в консоль и лог-файл
"""
async def display_info(coin: str, buy_exchange: str, sell_exchange: str, bid: Decimal, ask: Decimal, spread: Decimal) -> None:
    total = Decimal(100000)
    quantity = 0
    profit = 0
    try:
        if bid != 0:
            quantity = total * Decimal((100 - spread) / 100) / bid
        profit = round((quantity * bid) - (quantity * ask) * Decimal((100 - spread) / 100))
    except Exception as e:
        logger.error(f"Непредвиденная ошибка в функции display_info: {str(e)}", exc_info=True)

    logger.info(f'Нашел спред на монете {coin} между {sell_exchange} и {buy_exchange}')
    logger.info(f'Покупка на бирже {buy_exchange} по цене {ask}')
    logger.info(f'Продажа на бирже {sell_exchange} по цене {bid}')
    logger.info(f'Профит: {profit} $')
    logger.info('----------------------------------------')

