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

# (여기에 챗봇 엔드포인트 등 다른 코드가 있다면 그대로 둡니다)

# ─── 여기부터 파일 끝 부분 ──────────────────────────────

async def start_api():
    config = uvicorn.Config(health_app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    api_task = asyncio.create_task(start_api())
    bot_task = asyncio.create_task(run_bot_loop())
    await asyncio.gather(api_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
