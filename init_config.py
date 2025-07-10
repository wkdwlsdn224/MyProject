import json

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
config = {symbol: {"mode": "neutral", "min_score": 3} for symbol in symbols}

with open("strategy_config.json", "w") as f:
    json.dump(config, f, indent=2)
