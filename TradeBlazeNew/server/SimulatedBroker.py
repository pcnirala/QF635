import json
import logging

import zmq
import zmq.asyncio

import Config
from DataModels import *
from Decorator import *


@singleton
class SimulatedBroker:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._latest_prices = {}
        self._orders = []

        # ZeroMQ subscriber for market data
        ctx = zmq.asyncio.Context()
        self._market_socket = ctx.socket(zmq.SUB)
        if Config.MarketData.EnableConflation:
            self._market_socket.setsockopt(zmq.CONFLATE, 1)
        self._market_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self._market_socket.connect(Config.MarketData.ServerAddr)

    async def on_market_data(self):
        while True:
            msg = await self._market_socket.recv_string()
            market_data = MarketData(**json.loads(msg))
            self._latest_prices[market_data.ticker] = market_data.price

    async def place_order(self, order_data, on_order_execution):
        order_data.filled_price = self._latest_prices[order_data.ticker]
        order_data.order_status = 'FILLED'
        self._logger.info(f'Executed order: {order_data}')

        # async callback for notifying order execution
        await on_order_execution(order_data)
