# 📦 strategy.py — 전략 스코어 계산 모듈
import pandas as pd
import talib

def compute_ma_score(df):
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()

    if df["ma20"].iloc[-1] > df["ma50"].iloc[-1] and df["ma20"].iloc[-2] <= df["ma50"].iloc[-2]:
        return 1
    return 0

def compute_rsi_score(df):
    rsi = talib.RSI(df["close"], timeperiod=14)
    if rsi.iloc[-1] < 30 or rsi.iloc[-1] > 70:
        return 1
    return 0

def compute_macd_score(df):
    macd, signal, _ = talib.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        return 1
    return 0

def get_strategy_score(df):
    score = 0
    score += compute_ma_score(df)
    score += compute_rsi_score(df)
    score += compute_macd_score(df)
    return score
