from models import *
import asyncio
import sys
from internal import *


# Опционально для Windows
if sys.platform:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Исключения будем писать в лог целиком
@logger.catch()
async def main():
    async with OKX() as okx:
        await okx.get_prices()

    async with Binance() as binance:
        await binance.get_prices()

    async with Bybit() as bybit:
        await bybit.get_prices()

    task_1 = asyncio.create_task(update_coins_dicts(EXCHANGES_LIST))
    task_2 = asyncio.create_task(arbitrage(exchanges=EXCHANGES_LIST))

    await asyncio.gather(task_1, task_2)


asyncio.run(main())
