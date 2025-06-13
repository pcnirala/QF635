import asyncio
import json
import logging
from dataclasses import asdict

import pandas as pd
import zmq
import zmq.asyncio

import Config
from DataModels import *
from Decorator import *


class TradingStrategy:
    def __init__(self, name='Unnamed Strategy'):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._name = name
        self._prices = []

        # streaming pause/resume
        self._streaming_event = asyncio.Event()
        self._streaming_event.set()

        # ZeroMQ subscriber for market data
        ctx = zmq.asyncio.Context()
        self._market_socket = ctx.socket(zmq.SUB)

        # Enable conflation
        if Config.MarketData.EnableConflation:
            self._market_socket.setsockopt(zmq.CONFLATE, 1)
            self._logger.info('Conflation enabled for incoming market data ticks')

        # Set subscription filter (empty string = receive all messages)
        self._market_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        # Connect to market data publisher
        self._market_socket.connect(Config.MarketData.ServerAddr)

        # ZeroMQ publisher for signal data
        self._signal_socket = ctx.socket(zmq.PUSH)
        self._signal_socket.bind(Config.SignalData.ServerAddr)

        # ZeroMQ publisher for dashboard data
        self._xpub_socket = ctx.socket(zmq.PUB)
        self._xpub_socket.connect(Config.MessageBroker.XSubSocketAddr)  # Connect to broker XSUB port

    @staticmethod
    def get_instance():
        if Config.SignalData.Strategy == 'MACDStrategy':
            return MACDStrategy()
        else:
            raise ValueError(f'Invalid TradingStrategy: {Config.SignalData.Strategy}')

    def is_trading_engine_paused(self):
        return not self._streaming_event.is_set()

    def pause_trading_engine(self):
        self._streaming_event.clear()

    def resume_trading_engine(self):
        self._streaming_event.set()

    async def on_market_data(self):
        while True:
            msg = await self._market_socket.recv_string()

            # process this received market data only if trading engine is not paused
            if not self.is_trading_engine_paused():
                market_data = MarketData(**json.loads(msg))
                self._prices.append(market_data.price)

                signal, reason_dict = self._generate_signal()
                if signal:
                    signal_data = SignalData(timestamp=market_data.timestamp, ticker=market_data.ticker,
                                             price=market_data.price, action=signal)
                    self._logger.info(f'Sending: {signal_data}, {reason_dict}')

                    # send signal_data to MQ
                    await self._signal_socket.send_string(json.dumps(asdict(signal_data)))
                    await self._xpub_socket.send_string("SignalData: " + json.dumps(asdict(signal_data)))

            # Unlike await asyncio.sleep(0.01), this yields without a time cost.
            await asyncio.sleep(0)

    def _generate_signal(self):
        raise NotImplementedError('Subclasses must implement generate_signal')


@singleton
class MACDStrategy(TradingStrategy):
    def __init__(self, short_window=12, long_window=26, signal_window=9):
        super().__init__(name='MACD Strategy')
        self._short_window = short_window
        self._long_window = long_window
        self._signal_window = signal_window

        self._macd_df = None

    def _generate_signal(self):
        # Computes MACD, signal line, and histogram using pandas.
        if len(self._prices) < self._long_window:
            self._logger.info(
                f'Not enough data to compute MACD, available: {len(self._prices)}, required: {self._long_window}')
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

        if self._macd_df is None:
            self._macd_df = macd_df

        self._macd_df.loc[len(self._macd_df)] = macd_df.iloc[-1]

        prev = self._macd_df.iloc[-2]
        curr = self._macd_df.iloc[-1]

        signal = 'HOLD'
        if curr['MACD'] > curr['Signal'] and prev['MACD'] <= prev['Signal']:
            signal = 'BUY'
        elif curr['MACD'] < curr['Signal'] and prev['MACD'] >= prev['Signal']:
            signal = 'SELL'

        reason_dict = curr.to_dict()  # add more items in dict as needed for debugging
        return signal, curr.to_dict()
