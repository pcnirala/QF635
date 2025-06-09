import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Download AAPL price data
df = yf.download("AAPL", start="2022-01-01", end="2023-01-01")[["Close"]]

# Evaluation metrics
def compute_metrics(strategy_return, equity_curve):
    ann_ret = strategy_return.mean() * 252
    ann_vol = strategy_return.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0
    mdd = (equity_curve / equity_curve.cummax() - 1).min()
    return ann_ret, ann_vol, sharpe, mdd

# Calculate RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)

df["RSI"] = compute_rsi(df["Close"])

# Generate RSI signals
rsi_signal = []
rsi_position = 0
rsi_position_list = []
for rsi in df["RSI"]:
    if rsi < 48 and rsi_position == 0:
        rsi_signal.append("Buy")
        rsi_position = 1
    elif rsi > 52 and rsi_position == 1:
        rsi_signal.append("Sell")
        rsi_position = 0
    else:
        rsi_signal.append("Hold")
    rsi_position_list.append(rsi_position)

df["RSI_Signal"] = rsi_signal
df["RSI_Signal_Num"] = df["RSI_Signal"].map({"Buy": 1, "Sell": -1, "Hold": 0})
df["RSI_Position"] = rsi_position_list

# Calculate RSI strategy performance
df["Return"] = df["Close"].pct_change()
df["RSI_Strategy_Return"] = df["Return"] * df["RSI_Position"]
df["RSI_Equity"] = (1 + df["RSI_Strategy_Return"]).cumprod()

rsi_metrics = compute_metrics(df["RSI_Strategy_Return"], df["RSI_Equity"])
pnl = df["RSI_Equity"].iloc[-1] - 1  # Total P&L

# Plot RSI signals
plt.figure(figsize=(14, 5))
plt.plot(df.index, df["Close"], label="Close", color="black")
plt.scatter(df[df["RSI_Signal_Num"] == 1].index, df["Close"][df["RSI_Signal_Num"] == 1], color="green", marker="^", s=100, label="RSI Buy")
plt.scatter(df[df["RSI_Signal_Num"] == -1].index, df["Close"][df["RSI_Signal_Num"] == -1], color="red", marker="v", s=100, label="RSI Sell")
plt.title("RSI Buy/Sell Signals on AAPL")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Show RSI signal table
print("\n📋 RSI signal table (last 20 rows)")
print(df[["Close", "RSI", "RSI_Signal", "RSI_Signal_Num", "RSI_Position", "RSI_Equity"]].dropna().tail(20))

# Show RSI strategy metrics
print("\n📊 RSI Strategy Metrics:")
print(f"Annual Return:     {rsi_metrics[0]:.2%}")
print(f"Volatility:        {rsi_metrics[1]:.2%}")
print(f"Sharpe Ratio:      {rsi_metrics[2]:.2f}")
print(f"Max Drawdown:      {rsi_metrics[3]:.2%}")
print(f"Total P&L:         {pnl:.2%}")

# MACD calculation
def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

df["MACD"], df["MACD_Signal_Line"] = compute_macd(df["Close"])

# Generate MACD signals
macd_signal = []
macd_position = 0
macd_position_list = []
for macd, sig in zip(df["MACD"], df["MACD_Signal_Line"]):
    if macd > sig and macd_position == 0:
        macd_signal.append("Buy")
        macd_position = 1
    elif macd < sig and macd_position == 1:
        macd_signal.append("Sell")
        macd_position = 0
    else:
        macd_signal.append("Hold")
    macd_position_list.append(macd_position)

df["MACD_Signal"] = macd_signal
df["MACD_Signal_Num"] = df["MACD_Signal"].map({"Buy": 1, "Sell": -1, "Hold": 0})
df["MACD_Position"] = macd_position_list

# Calculate MACD strategy performance
df["MACD_Strategy_Return"] = df["Return"] * df["MACD_Position"]
df["MACD_Equity"] = (1 + df["MACD_Strategy_Return"]).cumprod()

macd_metrics = compute_metrics(df["MACD_Strategy_Return"], df["MACD_Equity"])
macd_pnl = df["MACD_Equity"].iloc[-1] - 1  # Total P&L

# Plot MACD signals
plt.figure(figsize=(14, 5))
plt.plot(df.index, df["Close"], label="Close", color="black")
plt.scatter(df[df["MACD_Signal_Num"] == 1].index, df["Close"][df["MACD_Signal_Num"] == 1], color="blue", marker="^", s=100, label="MACD Buy")
plt.scatter(df[df["MACD_Signal_Num"] == -1].index, df["Close"][df["MACD_Signal_Num"] == -1], color="orange", marker="v", s=100, label="MACD Sell")
plt.title("MACD Buy/Sell Signals on AAPL")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Show MACD signal table
print("\n📋 MACD signal table (last 20 rows)")
print(df[["Close", "MACD", "MACD_Signal", "MACD_Signal_Num", "MACD_Position", "MACD_Equity"]].dropna().tail(20))

# Show MACD strategy metrics
print("\n📊 MACD Strategy Metrics:")
print(f"Annual Return:     {macd_metrics[0]:.2%}")
print(f"Volatility:        {macd_metrics[1]:.2%}")
print(f"Sharpe Ratio:      {macd_metrics[2]:.2f}")
print(f"Max Drawdown:      {macd_metrics[3]:.2%}")
print(f"Total P&L:         {macd_pnl:.2%}")
