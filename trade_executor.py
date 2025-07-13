# trade_executor.py

import os
import time
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from utils import exception_notifier, send_telegram

load_dotenv()

class TradeExecutor:
    """
    Binance REST API를 사용해 시장가 주문(buy/sell)을 실행하는 클래스입니다.
    """
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.client = Client(api_key, api_secret)

    @exception_notifier
    def buy_market(self, symbol: str, quantity: float, retries: int = 3) -> Dict[str, Any]:
        for attempt in range(1, retries + 1):
            try:
                order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
                logging.info(f"[BUY_SUCCESS] {symbol} @ {quantity}")
                return order
            except (BinanceAPIException, BinanceOrderException) as e:
                logging.warning(f"[BUY_FAIL] {symbol} attempt {attempt}: {e}")
                if attempt == retries:
                    send_telegram(f"❌ 매수 실패: {symbol} x {quantity} → {e}")
                    raise
                time.sleep(2 ** attempt)

    @exception_notifier
    def sell_market(self, symbol: str, quantity: float, retries: int = 3) -> Dict[str, Any]:
        for attempt in range(1, retries + 1):
            try:
                order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
                logging.info(f"[SELL_SUCCESS] {symbol} @ {quantity}")
                return order
            except (BinanceAPIException, BinanceOrderException) as e:
                logging.warning(f"[SELL_FAIL] {symbol} attempt {attempt}: {e}")
                if attempt == retries:
                    send_telegram(f"❌ 매도 실패: {symbol} x {quantity} → {e}")
                    raise
                time.sleep(2 ** attempt)
        # 이럴 경우 거의 발생하지 않지만 안전장치
        raise RuntimeError(f"시장가 매도 실패: {symbol} x {quantity}")

async def your_trading_iteration(client_async) -> None:
    """
    run_bot_loop에서 호출하는 비동기 반복 함수입니다.
    여기서 client_async (AsyncClient)나
    TradeExecutor를 이용해 실제 거래 로직을 구현하세요.
    예시:
        executor = TradeExecutor(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET_KEY"))
        # 심볼·수량 산정 로직...
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            executor.buy_market,
            "BTCUSDT",
            0.001
        )
        print(f"[trading] executed: {result}")
    """
    # TODO: 실제 전략에 맞춰 아래 코드를 수정하세요.
    executor = TradeExecutor(
        os.getenv("BINANCE_API_KEY"),
        os.getenv("BINANCE_SECRET_KEY"),
    )

    # 예시 시장가 매수 (심볼과 수량은 실제 전략에 따라 동적으로 설정)
    symbol = "BTCUSDT"
    quantity = 0.001

    # sync 함수를 async로 호출
    try:
        order = await asyncio.get_event_loop().run_in_executor(
            None,
            executor.buy_market,
            symbol,
            quantity
        )
        logging.info(f"[TRADING] order: {order}")
    except Exception as e:
        logging.error(f"[TRADING_ERROR] {e}")
