# 📦 performance.py
import pandas as pd

def load_log_df(log_file="ultimate_trade_log.csv"):
    return pd.read_csv(log_file)

def adjust_strategy_mode(log_df):
    recent = log_df.tail(20)
    win_rate = len(recent[recent["PnL"] > 0]) / len(recent) if len(recent) else 0
    if win_rate > 0.7:
        return "aggressive"
    elif win_rate < 0.4:
        return "conservative"
    else:
        return "neutral"
