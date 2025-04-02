from typing import List
from models import Exchange
from logger import logger
from decimal import Decimal
# Пройтись по ключам из exchanges.coins и сравнить их
# Аск монеты текущей биржи должен быть меньше бида на другой бирже
# Бид монеты текущей биржи должен быть больше аска на другой бирже


async def arbitrage(exchanges: List[Exchange], spread: float=1, tax_fee: float=0.1):
    tickers = list(exchanges[0].coins.keys())

    for ticker in tickers:
        coin = ticker.replace('USDT', '')
        bids = []
        asks = []
        for exchange in exchanges:
            bids.append(Decimal(exchange.coins[ticker][0]))
            asks.append(Decimal(exchange.coins[ticker][1]))

        if (max(bids) * Decimal((100 - tax_fee) / 100)) / (min(asks) * (Decimal(100 + tax_fee) / 100)) > Decimal(spread / 100):
            max_bids_exchange = ''
            min_asks_exchange = ''
            for exchange in exchanges:
                if max(bids) == exchange.coins[ticker][0]:
                    max_bids_exchange = exchange.name.upper()
                if min(asks) == exchange.coins[ticker][1]:
                    min_asks_exchange = exchange.name.upper()

            await display_info(coin=coin, buy_exchange=min_asks_exchange, sell_exchange=max_bids_exchange,
                               bid=max(bids), ask=min(asks), spread=spread)


async def display_info(coin: str, buy_exchange: str, sell_exchange: str, bid: Decimal, ask: Decimal, spread: float) -> None:
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

