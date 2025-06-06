from types import SimpleNamespace

# Global configs
FEATURES = {
    "enable_short_sell": False,
    "mq_retry_attempts": 3
}

# Market related
MarketData = SimpleNamespace(
    Source="SimulatedDataSource",
    TickIntervalSeconds=0.5
)

# Strategy related
TRADING_STRATEGY = "MACDStrategy"
