# 📦 predict.py — 과거 흐름 기반 상승 예측 모듈
import pandas as pd
import numpy as np
import requests

def load_price_history(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=1000"
    try:
        res = requests.get(url).json()
        closes = [float(k[4]) for k in res]
        return closes
    except:
        return []

def predict_future(symbol):
    closes = load_price_history(symbol)
    if not closes or len(closes) < 100:
        return False  # 데이터 부족으로 예측 불가

    # 📈 단순한 상승 가능성 예측
    recent_trend = np.mean(np.diff(closes[-90:]))  # 최근 3달간 평균 변동폭
    volatility = np.std(closes[-90:])              # 변동성 계산

    if recent_trend > 0 and volatility < 10:
        return True  # 상승 추세 + 안정적이면 긍정 예측
    return False
