from types import SimpleNamespace

# Global configs
FEATURES = {
    "enable_short_sell": False,
    "mq_retry_attempts": 3
}

# Market related
MarketData = SimpleNamespace(
    EnableServerMode=False,

    Source="SimulatedDataSource",
    # Source="HistoricalDataSource",
    # Source="IBKRDataSource",

    # 1/0.05 = 20 messages per second
    # TickIntervalSeconds=0.01,
    # 1/0.1 = 10 messages per second
    # TickIntervalSeconds=0.1,
    # 1/0.5 = 2 messages per second
    TickIntervalSeconds=0.5,

    # Steam ticks for 600 sec only
    TickStreamDurationSeconds=600,
    # TickStreamDurationSeconds=30,

    EnableDuckDbPersistence=True,
    EnableCsvPersistence=True,

    ServerAddr="tcp://127.0.0.1:5555",
    EnableConflation=False
)

# Strategy related
SignalData = SimpleNamespace(
    Strategy="MACDStrategy",
    ServerAddr="tcp://127.0.0.1:5556"
)

# MessageBroker related
MessageBroker = SimpleNamespace(
    XSubSocketAddr="tcp://127.0.0.1:5557",
    XPubSocketAddr="tcp://127.0.0.1:5558"
)

# Order related
OrderData = SimpleNamespace(
    Name="Value"
)

# DB related
DB_COUNTER_PATH = "data/Counter.sqlite"
# Note that the max value of Counter/SEQ is 2^63-1 = 9.2 Million Trillion
DEFAULT_SEQ_START = 10_000_000
ORDER_SEQ_START = 30_000_000
TRADE_SEQ_START = 50_000_000

# Others
ENABLE_LIVE_TRADING = False
