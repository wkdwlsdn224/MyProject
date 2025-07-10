# 📦 risk.py — 변동성 기반 자동 레버리지 설정 모듈
import numpy as np
import aiohttp

async def fetch_prices(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h&limit=24"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()
            closes = [float(item[4]) for item in data]
            return closes

async def compute_leverage(symbol):
    prices = await fetch_prices(symbol)
    if not prices or len(prices) < 10:
        return 10  # 기본값

    volatility = np.std(prices)  # 표준편차로 변동성 계산

    if volatility > 100:
        return 5   # 고변동성 → 보수적 진입
    elif volatility > 50:
        return 10  # 중간 변동성
    else:
        return 15  # 안정적일수록 공격적 전략

def compute_leverage(symbol): ...
def get_dynamic_thresholds(volatility): ...
