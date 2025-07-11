#!/usr/bin/env python3
import os
import time
import asyncio
import logging
import threading

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# health_app 가져오기
from health import (
    app as health_app,
    order_counter,
    process_latency,
    error_counter,
    last_trade_pnl,
    pnl_distribution,
)
# 나머지 모듈 임포트
from binance.client import Client
from binance import AsyncClient

from config import API_KEY, API_SECRET, MIN_STRATEGY_SCORE, STRATEGY_MODE
from data_loader import load_candle_data
from logger import log_event, record_trade
from notifier import send_telegram, send_position_update
from strategy_engine import get_strategy_score, compute_leverage, get_dynamic_thresholds
from ml_engine import train_lstm, predict_future_lstm
from filters import get_reliable_symbols
from portfolio import Portfolio

# 로그 디렉터리 생성
LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# ─── 여기에 챗봇 엔드포인트 추가 ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@health_app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # TODO: 실제 챗봇 로직으로 교체하세요 (예: OpenAI API 호출)
    answer = f"Echo: {req.message}"
    return {"reply": answer}
# ────────────────────────────────────────────────────────────────────────────


async def process_symbol(client_sync, client_async, symbol, portfolio):
    try:
        # 처리 지연 측정
        with process_latency.labels(symbol=symbol).time():
            df = load_candle_data(client_sync, symbol, "1m", 100)
            score = get_strategy_score(df, STRATEGY_MODE)
            if score < MIN_STRATEGY_SCORE:
                return

            lev = compute_leverage(score)
            thresholds = get_dynamic_thresholds(df)
            threshold = (
                thresholds["aggressive"]
                if STRATEGY_MODE == "aggressive"
                else thresholds["conservative"]
            )

            model = train_lstm(df)
            prediction = predict_future_lstm(model, df)

            if prediction > threshold:
                order = await client_async.futures_create_order(
                    symbol=symbol,
                    side="BUY",
                    type="MARKET",
                    quantity=lev,
                )
                entry_price = float(order.get("avgFillPrice", 0))

                # 실제 운영 시에는 별도 exit_price 변수를 사용하세요
                exit_price = entry_price
                pnl_pct = (exit_price - entry_price) / entry_price * 100

                # 메트릭 갱신
                order_counter.labels(symbol=symbol).inc()
                last_trade_pnl.set(pnl_pct)
                pnl_distribution.observe(pnl_pct)

                # 로깅·알림
                record_trade(symbol, entry_price, "BUY", lev, pnl_pct)
                send_position_update(symbol, "LONG", entry_price, pnl=pnl_pct)
                log_event(
                    f"Entered LONG {symbol} @ {entry_price:.3f} → PnL: {pnl_pct:.2f}%",
                    level="SUCCESS"
                )
                portfolio.update_position(symbol, "LONG", entry_price)

    except Exception as e:
        error_counter.labels(symbol=symbol).inc()
        msg = f"Error in process_symbol({symbol}): {e}"
        log_event(msg, level="ERROR")
        send_telegram(f"🛑 {msg}")


async def main():
    client_sync = Client(API_KEY, API_SECRET)
    client_async = await AsyncClient.create(API_KEY, API_SECRET)

    send_telegram("🚀 Bot 시동 완료")
    log_event("봇 시동 완료", level="SUCCESS")

    symbols = await get_reliable_symbols(client_async)
    portfolio = Portfolio()
    await asyncio.gather(*[
        process_symbol(client_sync, client_async, sym, portfolio)
        for sym in symbols
    ])

    await client_async.close_connection()


if __name__ == "__main__":
    # 헬스·메트릭 서버 백그라운드 기동
    threading.Thread(
        target=lambda: uvicorn.run(
            health_app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        ),
        daemon=True
    ).start()

    # 메인 루프 (30초마다 실행)
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            msg = f"🌀 루프 오류 — 재시작: {e}"
            send_telegram(msg)
            log_event(msg, level="ERROR")
        time.sleep(30)
