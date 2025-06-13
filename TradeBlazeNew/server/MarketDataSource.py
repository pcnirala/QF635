import csv
import logging
from datetime import datetime

import numpy as np

import Config
from DataModels import *
from LoggingConfig import *


class MarketDataSource:
    def __init__(self, data_type="UnknownDataType", ticker="UnnamedTicker"):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._data_type = data_type
        self._ticker = ticker

    @property
    def data_type(self):
        return self._data_type

    @property
    def ticker(self):
        return self._ticker

    def next_price(self):
        raise NotImplementedError("Subclasses must implement next_price")

    @staticmethod
    def get_instance(ticker="SPY"):
        if Config.MarketData.Source == "SimulatedDataSource":
            return SimulatedDataSource(ticker)
        elif Config.MarketData.Source == "HistoricalDataSource":
            return HistoricalDataSource(ticker)
        elif Config.MarketData.Source == "IBKRDataSource":
            return IBKRDataSource(ticker)
        else:
            raise ValueError(f"Invalid MarketDataSource: {Config.MarketData.Source}")


class SimulatedDataSource(MarketDataSource):
    def __init__(self, ticker="SPY", start_price=500.0, mu=0.0001, sigma=0.01, seed=42):
        super().__init__(data_type="SimulatedData", ticker=ticker)
        self._price = start_price
        self._mu = mu
        self._sigma = sigma

        if seed is not None:
            np.random.seed(seed)
            self._logger.info(f"Using random number seed: {seed}")

    def next_price(self):
        dt = 1.0
        z = np.random.normal()
        drift = (self._mu - 0.5 * self._sigma ** 2) * dt
        diffusion = self._sigma * np.sqrt(dt) * z
        self._price *= np.exp(drift + diffusion)
        self._price = round(self._price, 2)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return MarketData(timestamp=timestamp, ticker=self._ticker, price=self._price)


class HistoricalDataSource(MarketDataSource):
    def __init__(self, ticker="SPY"):
        super().__init__(data_type="HistoricalData", ticker=ticker)

        csv_path = f"data/{self._ticker}_{self._data_type}Repo.csv"
        if not os.path.exists(csv_path):
            msg = f"File {csv_path} does not exist"
            self._logger.error(f"File {csv_path} does not exist")
            raise RuntimeError(msg)

        self._cvs_file = open(csv_path, newline='')
        self._csv_reader = csv.reader(self._cvs_file)
        row = next(self._csv_reader)  # Skip header: Timestamp,Ticker,Price
        if len(row) < 3:
            raise ValueError(f"Invalid row: {row}")

    def next_price(self):
        try:
            row = next(self._csv_reader)
            timestamp, ticker, price = row
            return MarketData(timestamp=timestamp, ticker=ticker, price=float(price))
        except StopIteration:
            self._logger.warning(f"File {self._cvs_file.name} exhausted")

        return None


class IBKRDataSource(MarketDataSource):
    def __init__(self, ticker="SPY"):
        super().__init__(data_type="IBKRData", ticker=ticker)

    def next_price(self):
        raise NotImplementedError(f"Not implemented: {Config.MarketData.Source}")
