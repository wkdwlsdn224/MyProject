import time
import logging
import requests
from requests.exceptions import RequestException

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
            logging.warning(f"[HTTP GET] {url} 시도 {attempt} 실패: {e}")
            if attempt == retries:
                logging.error(f"[HTTP GET] 최종 실패: {url}", exc_info=True)
                raise
            time.sleep(backoff * attempt)

# utils.py

import logging
from functools import wraps
import streamlit as st
from utils import send_telegram  # 또는 실제 send_telegram 경로로 조정

def exception_notifier(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 1) 로그에 스택트레이스 기록
            logging.error(f"[{func.__name__}] 예외 발생: {e}", exc_info=True)
            # 2) Telegram 알림
            try:
                send_telegram(f"🚨 Bot 오류: {func.__name__}\n{e}")
            except Exception:
                logging.error("Telegram 알림 전송 실패", exc_info=True)
            # 3) UI에 에러 표시
            st.error(f"시스템 오류가 발생했습니다: {e}")
            st.stop()
    return wrapper

# utils.py 상단
from dotenv import load_dotenv
import os

load_dotenv()

import requests
from binance.client import Client

# 기존 send_telegram, get_current_positions, get_current_price 함수가
# os.getenv("…") 로 키를 불러오게 됩니다.

# 📦 utils.py — 알림, 로그, 기록 처리 모듈
import csv
import os
import requests
from datetime import datetime

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram 알림 실패:", e)

def log_event(message: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("bot_log.txt", "a") as f:
        f.write(f"[{now}] {message}\n")

def record_trade(symbol, side, entry_price, exit_price, pnl):
    file = "ultimate_trade_log.csv"
    header = ["Time", "Symbol", "Side", "Entry", "Exit", "PnL"]

    if not os.path.exists(file):
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            side,
            round(entry_price, 2),
            round(exit_price, 2),
            f"{round(pnl * 100, 2)}%"
        ])

def send_telegram(msg): ...
def log_event(msg): ...
def record_trade(symbol, side, entry, exit, pnl): ...

def record_trade(symbol, side, entry, exit, pnl):
    # 기존 로그 저장 코드 ...
    update_symbol_performance(symbol, pnl)  # ✅ 성과 기록 추가

import requests

def send_telegram(message):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, data=payload)

import requests

def send_telegram(message):
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    return response.status_code == 200

import os
import requests

def send_telegram(message: str) -> bool:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": message})
    return resp.status_code == 200

def get_current_positions() -> list:
    # 예시: Binance API 호출 후 포지션 리스트 반환
    from binance.client import Client
    client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET_KEY"))
    # 실제 로직으로 대체하세요
    return client.futures_position_information()  

def get_current_price(symbol: str) -> float:
    from binance.client import Client
    client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET_KEY"))
    return float(client.get_symbol_ticker(symbol=symbol)["price"])
