import os
import csv
import time
import logging
from functools import wraps
from datetime import datetime

import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
import streamlit as st
from binance.client import Client


load_dotenv()


def http_get_with_retry(
    url: str,
    params: dict = None,
    retries: int = 3,
    backoff: float = 1.0
) -> requests.Response:
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            return resp
        except RequestException as e:
            logging.warning(f"[HTTP GET] {url} attempt {attempt} failed: {e}")
            if attempt == retries:
                logging.error(f"[HTTP GET] final failure: {url}", exc_info=True)
                raise
            time.sleep(backoff * attempt)


def exception_notifier(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"[{func.__name__}] exception: {e}", exc_info=True)
            try:
                send_telegram(f"🚨 Bot error in {func.__name__}: {e}")
            except Exception:
                logging.error("failed to send Telegram notification", exc_info=True)
            st.error(f"An error occurred: {e}")
            st.stop()
    return wrapper


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message: str) -> bool:
    """Send a message via Telegram bot. Returns True on HTTP 200."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram token or chat ID not set in environment")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        resp = requests.post(url, data=payload, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        logging.error(f"Telegram send failed: {e}", exc_info=True)
        return False


def log_event(message: str) -> None:
    """Append a timestamped event message to bot_log.txt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("bot_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")


def record_trade(
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    pnl: float
) -> None:
    """Record a completed trade to ultimate_trade_log.csv."""
    file_path = "ultimate_trade_log.csv"
    header = ["Time", "Symbol", "Side", "Entry", "Exit", "PnL"]

    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            side,
            round(entry_price, 2),
            round(exit_price, 2),
            f"{round(pnl * 100, 2)}%"
        ])


def get_current_positions() -> list:
    """Fetch current positions from Binance futures."""
    client = Client(
        os.getenv("BINANCE_API_KEY"),
        os.getenv("BINANCE_SECRET_KEY")
    )
    return client.futures_position_information()


def get_current_price(symbol: str) -> float:
    """Fetch current symbol price from Binance."""
    client = Client(
        os.getenv("BINANCE_API_KEY"),
        os.getenv("BINANCE_SECRET_KEY")
    )
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker.get("price", 0.0))
