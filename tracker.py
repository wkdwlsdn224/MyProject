# 📦 tracker.py
symbol_perf = {}

def update_symbol_performance(symbol, pnl):
    if symbol not in symbol_perf:
        symbol_perf[symbol] = {"wins": 0, "losses": 0, "total_pnl": 0}
    if pnl > 0:
        symbol_perf[symbol]["wins"] += 1
    else:
        symbol_perf[symbol]["losses"] += 1
    symbol_perf[symbol]["total_pnl"] += pnl

def get_symbol_performance(symbol):
    data = symbol_perf.get(symbol, {})
    trades = data.get("wins", 0) + data.get("losses", 0)
    avg_pnl = data["total_pnl"] / trades if trades else 0
    return {"trades": trades, "avg_pnl": round(avg_pnl, 2)}

import pandas as pd

def get_symbol_performance(symbol, log_file="ultimate_trade_log.csv"):
    df = pd.read_csv(log_file)
    df = df[df["Symbol"] == symbol]
    trades = len(df)
    avg_pnl = df["PnL"].mean() if trades else 0
    win_rate = len(df[df["PnL"] > 0]) / trades * 100 if trades else 0
    return {
        "avg_pnl": round(avg_pnl, 2),
        "win_rate": round(win_rate, 1),
        "trades": trades
    }
