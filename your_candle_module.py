# ✅ 파일: your_candle_module.py
import pandas as pd

async def load_candle_data(client, symbol: str, interval: str = "1h", limit: int = 100):
    klines = await client.get_klines(symbol=symbol, interval=interval, limit=limit)

    ohlcv = {
        "open": [float(k[1]) for k in klines],
        "high": [float(k[2]) for k in klines],
        "low":  [float(k[3]) for k in klines],
        "close":[float(k[4]) for k in klines],
        "volume":[float(k[5]) for k in klines]
    }

    df = pd.DataFrame(ohlcv)
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()
    df = df.bfill()
    return df

async def load_candle_data(client, symbol, interval, limit): ...
