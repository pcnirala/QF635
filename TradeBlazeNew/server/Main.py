from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Endpoints import *
from MarketDataGateway import *
from MessageBroker import *
from OrderManager import *
from SimulatedBroker import *
from TradingStrategy import *


async def main():
    LoggingConfig.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Trade Blaze server ..")

    message_broker = MessageBroker()
    trading_strategy = TradingStrategy.get_instance()
    order_manager = OrderManager()
    simulated_broker = SimulatedBroker()

    async_tasks = [
        # concurrent tasks
        message_broker.run(),
        trading_strategy.on_market_data(),
        order_manager.on_signal_data(),
        simulated_broker.on_market_data()

        # parallel tasks
        # asyncio.to_thread(asyncio.run, message_broker.run()),
        # asyncio.to_thread(asyncio.run, trading_strategy.on_market_data()),
        # asyncio.to_thread(asyncio.run, order_manager.on_signal_data()),
        # asyncio.to_thread(asyncio.run, simulated_broker.on_market_data())
    ]

    if not Config.MarketData.EnableServerMode:
        logger.info("MarketDataGateway is set to run in-process")
        market_data_source = MarketDataSource.get_instance()
        market_data_gateway = MarketDataGateway(market_data_source)
        async_tasks.append(market_data_gateway.stream_prices())
        # async_tasks.append(asyncio.to_thread(asyncio.run, market_data_gateway.stream_prices()))

    await asyncio.gather(*async_tasks)


@asynccontextmanager
async def lifespan(the_app: FastAPI):
    # Now all the business logic stuff
    task = asyncio.create_task(main())
    yield
    # (Optionally) Cleanup tasks
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# REST and Websocket API
app = FastAPI(lifespan=lifespan)

# CORS settings
origins = ["*"]  # Or restrict to the frontend's URL

# Note: CORS stands for Cross-Origin Resource Sharing.
# When we develop locally:
# The frontend (React) runs at http://localhost:3000
# The server (FastAPI) runs at http://localhost:8000
# These are different origins.
# Browsers block most requests from one origin to another by default for security.

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes and WebSocket endpoints from api.py
app.include_router(Endpoints.get_router())

if __name__ == "__main__":
    # (Optional: For running with `python Main.py`)
    import uvicorn

    uvicorn.run(
        "Main:app",  # Module name and FastAPI instance
        host="0.0.0.0",
        port=8000,
        reload=True  # Enables auto-reloading like `--reload`
    )
