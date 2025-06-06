import sys

from LoggingConfig import *
from MarketDataSource import *
from PositionManager import *
from TradingStrategy import *


async def main():
    LoggingConfig.setup_logging()

    market_data_source = MarketDataSource.get_instance()
    trading_strategy = TradingStrategy.get_instance()
    position_manager = PositionManager()

    async_tasks = [
        # concurrent tasks
        market_data_source.stream_prices(),
        trading_strategy.consume_market_data_ticks(),
        position_manager.consume_signal_data()

        # parallel tasks
        # asyncio.to_thread(asyncio.run, market_data_source.stream_prices()),
        # asyncio.to_thread(asyncio.run, trading_strategy.consume_market_data_ticks()),
        # asyncio.to_thread(asyncio.run, position_manager.consume_signal_data())
    ]
    await asyncio.gather(*async_tasks)

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
