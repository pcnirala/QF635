import json
import logging

import zmq.asyncio

import Config
from DataModels import *


class Dashboard:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._last_dashboard_data = Dashboard.get_sample_dashboard_data()

        # ZeroMQ subscriber for dashboard data
        context = zmq.asyncio.Context()
        self._xsub_socket = context.socket(zmq.SUB)
        self._xsub_socket.connect(Config.MessageBroker.XPubSocketAddr)  # Connect to broker XPUB port
        self._xsub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    def reset_dashboard_data(self):
        self._last_dashboard_data = Dashboard.get_sample_dashboard_data()

    def get_last_dashboard_data(self):
        return self._last_dashboard_data

    # Dashboard update logic
    async def get_realtime_dashboard_update(self):
        msg = await self._xsub_socket.recv_string()

        max_rows = 5
        if msg.startswith("MarketData:"):
            msg = msg.removeprefix("MarketData:")
            self._logger.info(f"[MarketData] Dashboard update: {msg}")
            self._last_dashboard_data["market_data_ticks"].insert(0, json.loads(msg))
            # return only the latest max_rows records as of now
            self._last_dashboard_data["market_data_ticks"] = self._last_dashboard_data["market_data_ticks"][:max_rows]

        elif msg.startswith("SignalData:"):
            msg = msg.removeprefix("SignalData:")
            self._logger.info(f"[SignalData] Dashboard update: {msg}")
            self._last_dashboard_data["signals"].insert(0, json.loads(msg))
            self._last_dashboard_data["signals"] = self._last_dashboard_data["signals"][:max_rows]

        elif msg.startswith("OrderData:"):
            msg = msg.removeprefix("OrderData:")
            self._logger.info(f"[OrderData] Dashboard update: {msg}")
            self._last_dashboard_data["orders"].insert(0, json.loads(msg))
            self._last_dashboard_data["orders"] = self._last_dashboard_data["orders"][:max_rows]

        elif msg.startswith("TradeData:"):
            msg = msg.removeprefix("TradeData:")
            self._logger.info(f"[TradeData] Dashboard update: {msg}")
            self._last_dashboard_data["trades"].insert(0, json.loads(msg))
            self._last_dashboard_data["trades"] = self._last_dashboard_data["trades"][:max_rows]

        elif msg.startswith("PositionData:"):
            msg = msg.removeprefix("PositionData:")
            self._logger.info(f"[PositionData] Dashboard update: {msg}")
            position_data_dict = json.loads(msg)
            self._last_dashboard_data["positions"] = [position_data_dict]

            position_data = PositionData(**position_data_dict)
            self._last_dashboard_data["realized_pnl"] = position_data.realized_pnl
            self._last_dashboard_data["unrealized_pnl"] = position_data.unrealized_pnl

        else:
            # Unrecognized topic
            self._logger.info(f"[UNKNOWN] Dashboard update: {msg}")

        return self._last_dashboard_data

    @staticmethod
    def get_sample_dashboard_data():
        # sample of a live data feed
        return {
            "market_data_ticks": [
                # {"timestamp": "2025-06-11 21:16:10.797", "ticker": 'SPY', "price": 543.21},
            ],
            "signals": [
                # {"timestamp": "2025-06-11 21:16:10.797", "ticker": 'SPY', "price": 543.21, "action": 'BUY'},
                # {"timestamp": "2025-06-11 21:16:12.797", "ticker": 'SPY', "price": 542.48, "action": 'HOLD'},
                # {"timestamp": "2025-06-11 21:16:13.797", "ticker": 'SPY', "price": 544.54, "action": 'SELL'},
            ],
            "orders": [
                # {"timestamp": "2025-06-11 21:16:10.797", "ticker": 'SPY', "side": 'BUY', "qty": 1,
                #  "order_status": 'FILLED', "filled_price": 544.10},
                # {"timestamp": "2025-06-11 21:16:13.797", "ticker": 'SPY', "side": 'SELL', "qty": 1,
                #  "order_status": 'FILLED', "filled_price": 544.50},
            ],
            "trades": [
                # {"timestamp": "2025-06-11 21:16:10.797", "ticker": 'SPY', "direction": 'LONG', "units": 1,
                #  "unit_price": 544.10},
                # {"timestamp": "2025-06-11 21:16:13.797", "ticker": 'SPY', "direction": 'SHORT', "units": 1,
                #  "unit_price": 544.50}
            ],
            "positions": [
                # {"timestamp": "2025-06-11 21:16:10.797", "ticker": '', "units": 0, "avg_unit_price": 0},
            ],

            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "pnl_std_dev": 0.0,
            "sharp_ratio": 0.0,
            "treynor_ratio": 0.0,
            "information_ratio": 0.0,
            "drawdown": 0.0,
            "max_drawdown": 0.0,
            "cagr": 0.0,
            "var_value": 0.0,
        }
