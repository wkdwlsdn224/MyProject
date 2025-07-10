import pandas as pd

def load_trade_log(path: str = "ultimate_trade_log.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["PnL (%)"] = df["PnL (%)"].astype(float)
    return df

def load_candle_data(
    client, symbol: str, interval: str, limit: int
) -> pd.DataFrame:
    """
    Binance API로 캔들 데이터 불러와 DataFrame 반환
    """
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "Open time", "Open", "High", "Low", "Close",
        "Volume", "Close time", *_])
    df["Close"] = df["Close"].astype(float)
    return df
