# bot.py

import asyncio
import logging

from binance import AsyncClient
from config import API_KEY, API_SECRET
from trade_executor import your_trading_iteration

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def run_bot_loop():
    if not API_KEY or not API_SECRET:
        logging.error("API_KEY/API_SECRET 환경변수가 설정되지 않았습니다.")
        return

    client_async = None
    while client_async is None:
        try:
            # 1) 테스트넷 연결: testnet=True 또는 base_endpoint 지정
            client_async = await AsyncClient.create(
                API_KEY,
                API_SECRET,
                testnet=True
                # 만약 base_endpoint를 직접 지정하고 싶다면:
                # base_endpoint="https://testnet.binance.vision"
            )
            logging.info("[bot] Binance 테스트넷 연결 성공")
        except Exception as e:
            logging.warning(f"[bot] Binance 테스트넷 연결 실패, 30초 뒤 재시도합니다: {e}")
            await asyncio.sleep(30)

    # 2) 필요한 초기화 코드 (예: 심볼 로딩 등)

    # 3) 본격적인 트레이딩 루프
    while True:
        try:
            await your_trading_iteration(client_async)
        except Exception as e:
            logging.error(f"[bot] 루프 중 오류 발생, 계속 실행합니다: {e}")
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run_bot_loop())
