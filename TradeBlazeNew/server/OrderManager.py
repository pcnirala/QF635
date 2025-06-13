import asyncio
from dataclasses import asdict

import zmq.asyncio

from Analytics import *
from OrderGateway import *


class OrderManager:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._order_gateway = OrderGateway(self._on_trade_data)
        self._order_counter = WALCounter("ORDER_SEQ")

        self._signals = []
        self._trades = []
        self._positions = {}

        self._lot_size = 1
        self._position_limit = 1

        # ZeroMQ subscriber for signal data
        ctx = zmq.asyncio.Context()
        self._signal_socket = ctx.socket(zmq.PULL)
        self._signal_socket.connect(Config.SignalData.ServerAddr)

        # ZeroMQ publisher for dashboard data
        self._xpub_socket = ctx.socket(zmq.PUB)
        self._xpub_socket.connect(Config.MessageBroker.XSubSocketAddr)  # Connect to broker XSUB port

    async def on_signal_data(self):
        while True:
            msg = await self._signal_socket.recv_string()
            signal_data = SignalData(**json.loads(msg))
            self._logger.info(f'Received signal data: {signal_data}')
            self._signals.append(signal_data)

            if signal_data.ticker not in self._positions:
                position_data = PositionData(timestamp=signal_data.timestamp, ticker=signal_data.ticker,
                                             units=0, avg_unit_price=0, realized_pnl=0, unrealized_pnl=0)
                # In preparation that there may be a deal later
                self._positions[signal_data.ticker] = position_data
            position_data = self._positions[signal_data.ticker]

            # update the pnl stats in position_data
            position_data.unrealized_pnl = (signal_data.price - position_data.avg_unit_price) * position_data.units
            position_data.unrealized_pnl = round(position_data.unrealized_pnl, 2)
            position_data.timestamp = signal_data.timestamp
            self._logger.info(f'Positions in portfolio: {self._positions}')

            # send to dashboard
            await self._xpub_socket.send_string("PositionData: " + json.dumps(asdict(position_data)))

            if self._can_place_order(signal_data, position_data):
                order_id = self._order_counter.next()
                order_data = OrderData(timestamp=signal_data.timestamp, order_id=order_id,
                                       ticker=signal_data.ticker,
                                       side=signal_data.action, qty=self._lot_size)
                await self._order_gateway.on_order_data(order_data)
                await self._xpub_socket.send_string("OrderData: " + json.dumps(asdict(order_data)))

            # Because this is `while True` loop, so need to prevent starvation!
            await asyncio.sleep(0)

    # is it fine to place an order?
    def _can_place_order(self, signal_data, position_data):
        insufficient_inventory = False
        can_cause_limit_breach = False

        if signal_data.action == 'SELL':
            if position_data.units < self._lot_size:
                insufficient_inventory = True
                self._logger.warning(f'Insufficient inventory for SELL order: {position_data}\n')
        elif signal_data.action == 'BUY':
            if position_data.units + self._lot_size > self._position_limit:
                can_cause_limit_breach = True
                self._logger.warning(f'Position limit reached for BUY order: {position_data}\n')

        is_hold_signal = signal_data.action == 'HOLD'
        return not (is_hold_signal or insufficient_inventory or can_cause_limit_breach)

    async def _on_trade_data(self, trade_data):
        self._trades.append(trade_data)
        self._logger.info(f'Trade count in portfolio: {len(self._trades)}')

        # send to dashboard
        await self._xpub_socket.send_string("TradeData: " + json.dumps(asdict(trade_data)))

        # update current position and stats
        position_data = self._positions[trade_data.ticker]
        position_data.timestamp = trade_data.timestamp

        # Algo assuming no short selling
        if trade_data.direction == 'LONG':
            total_cost = position_data.avg_unit_price * position_data.units + trade_data.unit_price * trade_data.units
            position_data.units += trade_data.units
            position_data.avg_unit_price = total_cost / position_data.units
        elif trade_data.direction == 'SHORT':
            position_data.realized_pnl += trade_data.units * (trade_data.unit_price - position_data.avg_unit_price)
            position_data.realized_pnl = round(position_data.realized_pnl, 2)
            position_data.units -= trade_data.units

        # Unrealized PnL
        position_data.unrealized_pnl = (trade_data.unit_price - position_data.avg_unit_price) * position_data.units
        position_data.unrealized_pnl = round(position_data.unrealized_pnl, 2)
        self._logger.info(f'Positions in portfolio: {self._positions}')

        # send to dashboard
        await self._xpub_socket.send_string("PositionData: " + json.dumps(asdict(position_data)))

        returns = self.compute_returns()
        sharpe = Analytics.sharpe_ratio(returns)
        daily_var = Analytics.historical_var(returns, portfolio_value=10000, confidence_level=0.95)
        self._logger.info(f'Sharpe Ratio: {sharpe:.2f}, 1-Day VaR: ${daily_var:.2f}\n')

    def compute_returns(self):
        returns = []
        position = None  # store (buy_price, timestamp)

        for trade_data in self._trades:
            price = float(trade_data.unit_price)
            if trade_data.direction == 'LONG':
                position = price
            elif trade_data.direction == 'SHORT' and position is not None:
                ret = (price - position) / position
                returns.append(ret)
                position = None  # close position

        return returns
