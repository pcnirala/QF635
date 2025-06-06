import numpy as np

class Analytics:
    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=5.0):  # second-level data
        freq_per_year = 3600 * 24 * 252

        returns = np.array(returns)
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / freq_per_year)
        mean = np.mean(excess_returns)
        std = np.std(excess_returns)
        return (mean / std) * np.sqrt(freq_per_year) if std != 0 else 0.0

    @staticmethod
    def historical_var(returns, portfolio_value=10000, confidence_level=0.95):
        # 6.5×3600 = 23,400 (Number of Seconds in a Typical U.S. Trading Day)
        scale_to_seconds = 23400

        # Use last 250 return values only
        last_returns = returns[-250:] if len(returns) >= 250 else returns

        if len(last_returns) == 0:
            return 0.0

        var_pct = np.percentile(last_returns, (1 - confidence_level) * 100)
        var_pct_scaled = var_pct * np.sqrt(scale_to_seconds)  # scale up to 1 day
        return -var_pct_scaled * portfolio_value

