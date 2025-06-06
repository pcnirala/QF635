import asyncio
import json
import logging

import pandas as pd
import zmq
import zmq.asyncio

import Config


class TradingStrategy:
    def __init__(self, name="Unnamed Strategy"):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._name = name
        self._prices = []

        # ZeroMQ subscriber for market data
        ctx = zmq.asyncio.Context()
        self._market_socket = ctx.socket(zmq.SUB)
        self._market_socket.connect("tcp://127.0.0.1:5555")
        self._market_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # ZeroMQ publisher for signal data
        self._signal_socket = ctx.socket(zmq.PUB)
        self._signal_socket.bind("tcp://127.0.0.1:5556")

    @staticmethod
    def get_instance():
        if Config.TRADING_STRATEGY == "MACDStrategy":
            return MACDStrategy()
        else:
            raise ValueError(f"Invalid TradingStrategy: {Config.TRADING_STRATEGY}")

    async def consume_market_data_ticks(self):
        while True:
            msg = await self._market_socket.recv_string()
            market_data_tick = json.loads(msg)
            timestamp = market_data_tick['Timestamp']
            ticker = market_data_tick['Ticker']
            price = market_data_tick["Price"]
            self._prices.append(price)

            signal, reason_dict = self._generate_signal()
            if signal:
                self._logger.debug(f"[{timestamp}] {self._name} Signal: {signal} @ {price}, {reason_dict}")

                # write trading_signal to MQ
                trading_signal = {
                    "Timestamp": timestamp,
                    "Ticker": ticker,
                    "Price": price,
                    "Action": signal
                }
                await self._signal_socket.send_string(json.dumps(trading_signal))

            # Unlike await asyncio.sleep(0.01), this yields without a time cost.
            await asyncio.sleep(0)

    def _generate_signal(self):
        raise NotImplementedError("Subclasses must implement generate_signal")


class MACDStrategy(TradingStrategy):
    def __init__(self, short_window=12, long_window=26, signal_window=9):
        super().__init__(name="MACD Strategy")
        self._short_window = short_window
        self._long_window = long_window
        self._signal_window = signal_window

    def _generate_signal(self):
        """
        Computes MACD, signal line, and histogram using pandas.
        Returns a DataFrame containing all values.
        """
        if len(self._prices) < self._long_window:
            self._logger.info(
                f"Not enough data to compute MACD, available: {len(self._prices)}, required: {self._long_window}")
            return None, None

        prices = pd.Series(self._prices[-self._long_window:], dtype='float64')

        ema_short = prices.ewm(span=self._short_window, adjust=False).mean()
        ema_long = prices.ewm(span=self._long_window, adjust=False).mean()
        macd_line = ema_short - ema_long
        macd_line = round(macd_line, 2)
        signal_line = macd_line.ewm(span=self._signal_window, adjust=False).mean()
        signal_line = round(signal_line, 2)
        # histogram = macd_line - signal_line

        macd_df = pd.DataFrame({
            'Price': prices,
            'MACD': macd_line,
            'Signal': signal_line,
            # 'Histogram': histogram
        })

        prev = macd_df.iloc[-2]
        curr = macd_df.iloc[-1]

        signal = "HOLD"
        if curr['MACD'] > curr['Signal'] and prev['MACD'] <= prev['Signal']:
            signal = "BUY"
        elif curr['MACD'] < curr['Signal'] and prev['MACD'] >= prev['Signal']:
            signal = "SELL"

        return signal, curr.to_dict()
