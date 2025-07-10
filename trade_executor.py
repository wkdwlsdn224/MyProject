import os
import time
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from dotenv import load_dotenv
from utils import exception_notifier, send_telegram

load_dotenv()

class TradeExecutor:
    def __init__(self):
        key    = os.getenv("BINANCE_API_KEY")
        secret = os.getenv("BINANCE_SECRET_KEY")
        self.client = Client(key, secret)

    @exception_notifier
    def buy_market(self, symbol: str, quantity: float, retries: int = 3):
        for i in range(1, retries + 1):
            try:
                order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
                logging.info(f"[BUY] {symbol}@{quantity} 성공")
                return order
            except (BinanceAPIException, BinanceOrderException) as e:
                logging.warning(f"[BUY] {symbol} 시도 {i} 실패: {e}")
                if i == retries:
                    send_telegram(f"❌ 매수 실패: {symbol} x {quantity} → {e}")
                    raise
                time.sleep(2 ** i)

    @exception_notifier
    def sell_market(self, symbol: str, quantity: float, retries: int = 3):
        for i in range(1, retries + 1):
            try:
                order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
                logging.info(f"[SELL] {symbol}@{quantity} 성공")
                return order
            except (BinanceAPIException, BinanceOrderException) as e:
                logging.warning(f"[SELL] {symbol} 시도 {i} 실패: {e}")
                if i == retries:
                    send_telegram(f"❌ 매도 실패: {symbol} x {quantity} → {e}")
                    raise
                time.sleep(2 ** i)

# trade_executor.py 상단
from dotenv import load_dotenv
import os

from binance.client import Client
import time

load_dotenv()

class TradeExecutor:
    def __init__(self):
        api_key    = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_SECRET_KEY")
        self.client = Client(api_key, api_secret)
    # …

import time
from binance.client import Client
from typing import Dict, Any

class TradeExecutor:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.client = Client(api_key, api_secret)

    def buy_market(
        self, symbol: str, quantity: float, retries: int = 3
    ) -> Dict[str, Any]:
        """
        시장가 매수. 실패 시 지연 후 재시도.
        """
        for attempt in range(1, retries + 1):
            try:
                return self.client.order_market_buy(
                    symbol=symbol, quantity=quantity
                )
            except Exception as e:
                if attempt == retries:
                    raise
                time.sleep(2 ** attempt)

    def sell_market(
        self, symbol: str, quantity: float, retries: int = 3
    ) -> Dict[str, Any]:
        for attempt in range(1, retries + 1):
            try:
                return self.client.order_market_sell(
                    symbol=symbol, quantity=quantity
                )
            except Exception:
                time.sleep(2 ** attempt)
        raise RuntimeError("자동 청산 실패")
