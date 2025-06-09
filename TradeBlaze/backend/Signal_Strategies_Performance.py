import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_strategy_results(ticker, strategy_data, strategy_name,
                          short_window=20, long_window=50,  # MA parameter
                          fast=12, slow=26, signal=9):  # MACD parameter
    df = strategy_data[ticker]

    plt.figure(figsize=(15, 12))
    plt.suptitle(f"{ticker} {strategy_name} Strategy Results", y=1.02)

    # price and signals
    plt.subplot(3, 1, 1)
    plt.plot(df['price'], label='Price', color='black', alpha=0.8)

    if strategy_name == 'MA Crossover':
        plt.plot(df['MA_short'], label=f'MA {short_window}', color='blue')
        plt.plot(df['MA_long'], label=f'MA {long_window}', color='red')
    elif strategy_name == 'Bollinger Bands':
        plt.plot(df['MA'], label='Middle Band', color='blue')
        plt.plot(df['Upper_Band'], label='Upper Band', color='red', linestyle='--')
        plt.plot(df['Lower_Band'], label='Lower Band', color='green', linestyle='--')
    elif strategy_name == 'RSI':
        plt.plot(df.index, [30] * len(df), label='RSI Buy (30)', color='green', linestyle=':')
        plt.plot(df.index, [70] * len(df), label='RSI Sell (70)', color='red', linestyle=':')
    elif strategy_name == 'MACD':
        plt.plot(df['EMA_fast'], label=f'EMA {fast}', color='royalblue')
        plt.plot(df['EMA_slow'], label=f'EMA {slow}', color='darkorange')

    # Unify the trading signal marking
    buy_signals = df[df['Signal'] == 1]
    sell_signals = df[df['Signal'] == -1]
    plt.scatter(buy_signals.index, buy_signals['price'],
                marker='^', color='limegreen', s=100, alpha=1, label='Buy')
    plt.scatter(sell_signals.index, sell_signals['price'],
                marker='v', color='crimson', s=100, alpha=1, label='Sell')

    plt.ylabel('Price')
    plt.legend(loc='upper left')
    plt.grid(alpha=0.3)

    # MACD indicators
    if strategy_name == 'MACD':
        plt.subplot(3, 1, 2)
        plt.plot(df['MACD'], label='MACD', color='blue')
        plt.plot(df['MACD_signal'], label='Signal Line', color='orange')
        plt.axhline(0, color='black', linestyle='-', alpha=0.3)

        # difference value
        plt.bar(df.index, df['MACD'] - df['MACD_signal'],
                color=np.where(df['MACD'] > df['MACD_signal'], 'limegreen', 'tomato'),
                alpha=0.5, label='Histogram')

        plt.ylabel('MACD')
        plt.legend(loc='upper left')
        plt.grid(alpha=0.3)

    # cumulative return rate
    plot_idx = 3 if strategy_name == 'MACD' else 2
    plt.subplot(3, 1, plot_idx)
    plt.plot(df['cumulative_market_return'],
             label='Buy & Hold', color='black', alpha=0.8)
    plt.plot(df['cumulative_strategy_return'],
             label='Strategy', color='blue', alpha=0.8)

    plt.ylabel('Cumulative Return')
    plt.legend(loc='upper left')
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def calculate_performance_metrics(strategy_data, strategy_name):
    performance = {}

    for ticker, df in strategy_data.items():
        annual_return = df['strategy_return'].mean() * 252
        annual_volatility = df['strategy_return'].std() * np.sqrt(252)
        # risk-free = 0
        sharpe_ratio = annual_return / annual_volatility
        max_drawdown = df['drawdown'].max()

        performance[ticker] = {
            'Annual Return': annual_return,
            'Annual Volatility': annual_volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown
        }

    performance_df = pd.DataFrame(performance).T
    performance_df.index.name = 'Ticker'
    performance_df.columns.name = strategy_name
    return performance_df