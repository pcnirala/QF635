from DbUtils import *
from SimulatedBroker import *


class OrderGateway:
    def __init__(self, on_trade_data):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._simulated_broker = SimulatedBroker()
        self._on_trade_data = on_trade_data

        self._trade_counter = WALCounter("TRADE_SEQ")

        self._orders = []

    async def on_order_data(self, order_data: OrderData):
        self._logger.info(f'Received order data: {order_data}')
        self._orders.append(order_data)

        await self._simulated_broker.place_order(order_data, self._on_order_execution)

    async def _on_order_execution(self, order_data):
        trade_id = self._trade_counter.next()
        trade_data = TradeData(timestamp=order_data.timestamp, trade_id=trade_id,
                               order_id=order_data.order_id, ticker=order_data.ticker,
                               units=order_data.qty, unit_price=order_data.filled_price,
                               direction='LONG' if order_data.side == 'BUY' else 'SHORT')

        self._logger.info(f'Deal done: {trade_data}')

        # async callback for notifying order execution
        await self._on_trade_data(trade_data)
