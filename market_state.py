def classify_market(df):
    recent_trend = df["close"].iloc[-1] - df["close"].iloc[-20]
    volatility = df["close"].rolling(20).std().iloc[-1]

    if recent_trend > 2 * volatility:
        return "bullish"
    elif recent_trend < -2 * volatility:
        return "bearish"
    else:
        return "sideways"
