import asyncio
import json
import logging

import zmq
import zmq.asyncio

from Analytics import *


class PositionManager:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._signals = []

        # ZeroMQ subscriber for signal data
        ctx = zmq.asyncio.Context()
        self._signal_socket = ctx.socket(zmq.SUB)
        self._signal_socket.connect("tcp://127.0.0.1:5556")
        self._signal_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    async def consume_signal_data(self):
        while True:
            msg = await self._signal_socket.recv_string()
            signal_data = json.loads(msg)
            self._logger.info(f"Received signal data: {signal_data}")

            timestamp = signal_data['Timestamp']
            ticker = signal_data["Ticker"]
            price = signal_data["Price"]
            action = signal_data["Action"]

            self._signals.append(signal_data)
            returns = self.compute_returns()

            sharpe = Analytics.sharpe_ratio(returns)
            daily_var = Analytics.historical_var(returns, portfolio_value=10000, confidence_level=0.95)
            self._logger.info(f"Sharpe Ratio: {sharpe:.2f}, 1-Day VaR: ${daily_var:.2f}")

            # Because this is `while True` loop, so need to prevent starvation!
            await asyncio.sleep(0)

    def compute_returns(self):
        returns = []
        position = None  # store (buy_price, timestamp)

        for signal in self._signals:
            action = signal['Action'].upper()
            price = float(signal['Price'])

            if action == 'BUY':
                position = price
            elif action == 'SELL' and position is not None:
                ret = (price - position) / position
                returns.append(ret)
                position = None  # close position

        return returns

# def calculate_sharpe(returns, risk_free_rate=0.0, freq_per_year=31536000):
#     excess_returns = np.array(returns) - (risk_free_rate / freq_per_year)
#     avg_excess = np.mean(excess_returns)
#     std_dev = np.std(excess_returns)
#     sharpe_ratio = (avg_excess / std_dev) * np.sqrt(freq_per_year)
#     return sharpe_ratio
#
