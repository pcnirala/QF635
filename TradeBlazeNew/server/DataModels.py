from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class MarketData:
    timestamp: str
    ticker: str
    price: float


@dataclass
class SignalData:
    timestamp: str
    ticker: str
    price: float
    action: str  # BUY, SELL, HOLD


@dataclass
class OrderData:
    timestamp: str
    order_id: int
    ticker: str
    side: str  # BUY, SELL
    qty: float = 1
    order_type: str = 'MARKET'  # MARKET, LIMIT
    order_status: str = 'NEW'  # NEW, FILLED, CANCELLED
    filled_price: float = None


@dataclass
class TradeData:
    timestamp: str
    trade_id: int
    order_id: int
    ticker: str
    direction: str  # LONG, SHORT
    units: float
    unit_price: float


@dataclass
class PositionData:
    timestamp: str
    ticker: str
    units: float  # can be negative
    avg_unit_price: float
    realized_pnl: float
    unrealized_pnl: float


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: str
    is_trading_engine_paused: bool = False
