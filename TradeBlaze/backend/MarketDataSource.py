import asyncio
import csv
import json
import logging
import os
import time
from datetime import datetime

import duckdb
import numpy as np
import zmq
import zmq.asyncio

import Config


class MarketDataSource:
    def __init__(self, name="UnnamedDataSource", ticker="UnnamedTicker"):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._name = name
        self._ticker = ticker
        self._tick_interval_seconds = Config.MarketData.TickIntervalSeconds

        db_path = f"data/{ticker}_simulated_data.duckdb"
        self._duckdb_conn = duckdb.connect(db_path)
        self._init_db()

        csv_path = f"data/{ticker}_simulated_data.csv"
        self._cvs_file = None
        self._csv_writer = None
        self._init_csv(csv_path)

        # ZeroMQ publisher for market data
        ctx = zmq.asyncio.Context()
        self._market_socket = ctx.socket(zmq.PUB)
        self._market_socket.bind("tcp://127.0.0.1:5555")

    @staticmethod
    def get_instance(ticker="SPY"):
        if Config.MarketData.Source == "SimulatedDataSource":
            return SimulatedDataSource(ticker)
        elif Config.MarketData.Source == "HistoricalDataSource":
            raise ValueError(f"Not implemented: {Config.MarketData.Source}")
        elif Config.MarketData.Source == "IBKRDataSource":
            raise ValueError(f"Not implemented: {Config.MarketData.Source}")
        else:
            raise ValueError(f"Invalid MarketDataSource: {Config.MarketData.Source}")

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

    def _next_price(self):
        raise NotImplementedError("Subclasses must implement next_price")

    async def stream_prices(self, duration_seconds=600):
        self._logger.info(f"Starting {self._name} stream for {self._ticker}...")
        start_time = time.time()
        try:
            while time.time() - start_time < duration_seconds:
                price = self._next_price()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                tick = {
                    "Timestamp": timestamp,
                    "Ticker": self._ticker,
                    "Price": price
                }
                await self._market_socket.send_string(json.dumps(tick))

                # Save to DuckDB
                self._duckdb_conn.execute(
                    "INSERT INTO ticks VALUES (?, ?, ?)",
                    (timestamp, self._ticker, price)
                )

                # Log to CSV
                self._csv_writer.writerow([timestamp, self._ticker, price])

                self._logger.debug(f"[{timestamp}] {self._name} {self._ticker}: ${price:.2f}")
                await asyncio.sleep(self._tick_interval_seconds)
        except KeyboardInterrupt:
            self._logger.info(f"{self._name} stopped.")
        finally:
            self._duckdb_conn.close()
            self._cvs_file.close()


class SimulatedDataSource(MarketDataSource):
    def __init__(self, ticker="SPY", start_price=500.0, mu=0.0001, sigma=0.01, seed=42):
        super().__init__(name="SimulatedDataSource", ticker=ticker)
        self._price = start_price
        self._mu = mu
        self._sigma = sigma

        if seed is not None:
            np.random.seed(seed)

    def _next_price(self):
        dt = 1.0
        z = np.random.normal()
        drift = (self._mu - 0.5 * self._sigma ** 2) * dt
        diffusion = self._sigma * np.sqrt(dt) * z
        self._price *= np.exp(drift + diffusion)
        self._price = round(self._price, 2)
        return self._price


# Example usage
async def main():
    data_source = SimulatedDataSource(ticker="SPY")
    await asyncio.gather(
        data_source.stream_prices(duration_seconds=30)
    )

# asyncio.run(main())
