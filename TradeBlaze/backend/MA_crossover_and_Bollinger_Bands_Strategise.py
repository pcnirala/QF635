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

class MACrossoverStrategy(TradingStrategy):
    def __init__(self, short_window=20, long_window=50):
        super().__init__(name="MA Crossover Strategy")
        self._short_window = short_window
        self._long_window = long_window
        self._df = pd.DataFrame(columns=['price'])

    def _generate_signal(self):
        if len(self._prices) < self._long_window:
            self._logger.info(
                f"Not enough data to compute MA Crossover, available: {len(self._prices)}, required: {self._long_window}")
            return None, None

        # Update DataFrame with latest prices
        self._df = pd.DataFrame({'price': self._prices[-self._long_window:]})

        # Calculate moving averages
        self._df['MA_short'] = self._df['price'].rolling(window=self._short_window).mean()
        self._df['MA_long'] = self._df['price'].rolling(window=self._long_window).mean()

        # Generate signal
        signal = "HOLD"
        if len(self._df) >= 2:  # Need at least 2 data points to compare
            prev_short = self._df['MA_short'].iloc[-2]
            prev_long = self._df['MA_long'].iloc[-2]
            curr_short = self._df['MA_short'].iloc[-1]
            curr_long = self._df['MA_long'].iloc[-1]

            if curr_short > curr_long and prev_short <= prev_long:
                signal = "BUY"
            elif curr_short < curr_long and prev_short >= prev_long:
                signal = "SELL"

        # Prepare reason dictionary
        reason_dict = {
            'Price': self._df['price'].iloc[-1],
            'MA_short': self._df['MA_short'].iloc[-1],
            'MA_long': self._df['MA_long'].iloc[-1]
        }

        return signal, reason_dict

class BollingerBandsStrategy(TradingStrategy):
    def __init__(self, window=20, num_std=2):
        super().__init__(name="Bollinger Bands Strategy")
        self._window = window
        self._num_std = num_std
        self._df = pd.DataFrame(columns=['price'])

    def _generate_signal(self):
        if len(self._prices) < self._window:
            self._logger.info(
                f"Not enough data to compute Bollinger Bands, available: {len(self._prices)}, required: {self._window}")
            return None, None

        # Update DataFrame with latest prices
        self._df = pd.DataFrame({'price': self._prices[-self._window:]})

        # Calculate Bollinger Bands
        self._df['MA'] = self._df['price'].rolling(window=self._window).mean()
        rolling_std = self._df['price'].rolling(window=self._window).std()
        self._df['Upper_Band'] = self._df['MA'] + self._num_std * rolling_std
        self._df['Lower_Band'] = self._df['MA'] - self._num_std * rolling_std

        # Generate signal
        signal = "HOLD"
        current_price = self._df['price'].iloc[-1]
        upper_band = self._df['Upper_Band'].iloc[-1]
        lower_band = self._df['Lower_Band'].iloc[-1]

        if current_price > upper_band:
            signal = "SELL"
        elif current_price < lower_band:
            signal = "BUY"

        # Prepare reason dictionary
        reason_dict = {
            'Price': current_price,
            'MA': self._df['MA'].iloc[-1],
            'Upper_Band': upper_band,
            'Lower_Band': lower_band
        }

        return signal, reason_dict