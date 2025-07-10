from ta import momentum, trend, volatility

def enrich(df):
    df["rsi"]       = momentum.rsi(df["close"],14)
    macd            = trend.MACD(df["close"])
    df["macd_hist"] = macd.macd_diff()
    bb              = volatility.BollingerBands(df["close"])
    df["bb_hi"]     = bb.bollinger_hband()
    df["bb_lo"]     = bb.bollinger_lband()
    df["ema20"]     = trend.ema_indicator(df["close"],20)
    df["ema50"]     = trend.ema_indicator(df["close"],50)
    return df

def check_flags(df, long=True):
    flags = []

    rsi_cond = df["rsi"].iloc[-1] < 40 if long else df["rsi"].iloc[-1] > 60
    flags.append(rsi_cond)

    macd_cond = df["macd_hist"].iloc[-1] > 0 if long else df["macd_hist"].iloc[-1] < 0
    flags.append(macd_cond)

    bb_cond = df["close"].iloc[-1] < df["bb_lo"].iloc[-1] if long else df["close"].iloc[-1] > df["bb_hi"].iloc[-1]
    flags.append(bb_cond)

    ema_cond = df["ema20"].iloc[-1] > df["ema50"].iloc[-1] if long else df["ema20"].iloc[-1] < df["ema50"].iloc[-1]
    flags.append(ema_cond)

    recent = df["close"].iloc[-3:]
    monotone_cond = recent.is_monotonic_increasing if long else recent.is_monotonic_decreasing
    flags.append(monotone_cond)

    return sum(flags) >= 2

def compute_ma_score(df): ...
def compute_rsi_score(df): ...
def compute_macd_score(df): ...

def get_strategy_score(df):
    score = 0
    score += compute_ma_score(df)
    score += compute_rsi_score(df)
    score += compute_macd_score(df)
    return score

import pandas as pd
import json

def optimize_strategy_config(log_file="ultimate_trade_log.csv", config_file="strategy_config.json"):
    df = pd.read_csv(log_file)
    df["PnL (%)"] = df["PnL (%)"].astype(float)

    with open(config_file, "r") as f:
        config = json.load(f)

    for symbol in df["Symbol"].unique():
        sub = df[df["Symbol"] == symbol]
        if len(sub) < 10:
            continue  # 데이터 부족 시 스킵

        win_rate = len(sub[sub["PnL (%)"] > 0]) / len(sub) * 100
        avg_pnl = sub["PnL (%)"].mean()

        # 전략 모드 조정
        if win_rate < 40 or avg_pnl < 0:
            new_mode = "conservative"
        elif win_rate < 60:
            new_mode = "neutral"
        else:
            new_mode = "aggressive"

        config[symbol]["mode"] = new_mode
        config[symbol]["min_score"] = round(avg_pnl, 2)

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    return config
