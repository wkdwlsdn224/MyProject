import logging
import csv
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_event(message: str, level: str = "INFO") -> None:
    if level == "ERROR":
        logging.error(message)
    else:
        logging.info(message)

def record_trade(symbol: str, entry_price: float, side: str, leverage: int, pnl: float) -> None:
    with open("trade_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), symbol, side, entry_price, leverage, pnl])
