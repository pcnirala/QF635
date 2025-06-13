import asyncio
import json
import sys
import time
from dataclasses import asdict

import duckdb
import zmq.asyncio

from MarketDataSource import *


class MarketDataGateway:
    def __init__(self, market_data_source):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._market_data_source = market_data_source

        self._data_type = market_data_source.data_type
        self._ticker = market_data_source.ticker

        self._tick_interval_seconds = Config.MarketData.TickIntervalSeconds

        db_path = f"data/{self._ticker}_{self._data_type}.duckdb"
        self._duckdb_conn = duckdb.connect(db_path)
        self._init_db()

        csv_path = f"data/{self._ticker}_{self._data_type}.csv"
        self._cvs_file = None
        self._csv_writer = None
        self._init_csv(csv_path)

        # ZeroMQ publisher for market data
        ctx = zmq.asyncio.Context()
        self._market_socket = ctx.socket(zmq.PUB)
        self._market_socket.bind(Config.MarketData.ServerAddr)

        # ZeroMQ publisher for dashboard data
        self._xpub_socket = ctx.socket(zmq.PUB)
        self._xpub_socket.connect(Config.MessageBroker.XSubSocketAddr)  # Connect to broker XSUB port

    def _init_db(self):
        self._duckdb_conn.execute("""
                                  CREATE TABLE IF NOT EXISTS ticks
                                  (
                                      Timestamp
                                      TIMESTAMP,
                                      Ticker
                                      TEXT,
                                      Price
                                      DOUBLE
                                  )
                                  """)

    def _init_csv(self, csv_path):
        if not os.path.exists(csv_path):
            self._cvs_file = open(csv_path, mode='w', newline='', buffering=1)
            self._csv_writer = csv.writer(self._cvs_file)
            self._csv_writer.writerow(['Timestamp', 'Ticker', 'Price'])
        else:
            self._cvs_file = open(csv_path, mode='a', newline='', buffering=1)
            self._csv_writer = csv.writer(self._cvs_file)

    async def stream_prices(self):
        self._logger.info(f"Running {self._ticker} {self._data_type} stream "
                          f"for {Config.MarketData.TickStreamDurationSeconds} seconds, "
                          f"sending one tick every {self._tick_interval_seconds} second ..")
        start_time = time.time()
        try:
            while time.time() - start_time < Config.MarketData.TickStreamDurationSeconds:
                market_data = self._market_data_source.next_price()
                if market_data is None:
                    self._logger.info(f"No more market data tick available")
                    break

                # Send tick to MQ
                await self._market_socket.send_string(json.dumps(asdict(market_data)))
                await self._xpub_socket.send_string("MarketData: " + json.dumps(asdict(market_data)))
                self._logger.info(f"Sent market data tick {self._ticker}: ${market_data.price:.2f}")

                # Save to DuckDB
                if Config.MarketData.EnableDuckDbPersistence:
                    self._duckdb_conn.execute(
                        "INSERT INTO ticks VALUES (?, ?, ?)",
                        (market_data.timestamp, self._ticker, market_data.price)
                    )

                # Log to CSV
                if Config.MarketData.EnableCsvPersistence:
                    self._csv_writer.writerow([market_data.timestamp, self._ticker, market_data.price])

                # wait until the configured interval
                await asyncio.sleep(self._tick_interval_seconds)

            self._logger.info(f"Streaming stopped after {round(time.time() - start_time, 2)} seconds")
        except KeyboardInterrupt:
            self._logger.info(f"Streaming stopped due to keyboard interrupt")
        finally:
            self._duckdb_conn.close()
            self._cvs_file.close()


# Example usage
async def main():
    LoggingConfig.setup_logging()
    logger = logging.getLogger(__name__)

    if not Config.MarketData.EnableServerMode:
        logger.info('MarketDataGateway ServerMode not configured.')
        return
    else:
        market_data_source = MarketDataSource.get_instance()
        market_data_gateway = MarketDataGateway(market_data_source)
        await asyncio.gather(
            market_data_gateway.stream_prices()
        )


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
