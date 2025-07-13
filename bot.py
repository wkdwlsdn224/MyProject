# bot.py

import asyncio
from binance import AsyncClient

# 환경변수로부터 API 키·시크릿 불러오기
from config import API_KEY, API_SECRET

# … 나머지 import

async def run_bot_loop():
    # 1) 먼저 AsyncClient 생성 실패를 재시도
    client_async = None
    while client_async is None:
        try:
            client_async = await AsyncClient.create(API_KEY, API_SECRET)
        except Exception as e:
            # 로그에 남기고 30초 뒤에 재시도
            print(f"[bot] Binance 연결 실패, 30초 뒤 재시도합니다: {e}")
            await asyncio.sleep(30)

    # 2) 클라이언트 생성 후 나머지 초기화
    # … (기존 초기화 코드)

    # 3) 본격적인 트레이딩 루프
    while True:
        try:
            # your_trading_iteration 는 실제 트레이딩 함수로 대체
            await your_trading_iteration(client_async)
        except Exception as e:
            print(f"[bot] 루프 중 오류, 계속 실행합니다: {e}")
        await asyncio.sleep(30)
