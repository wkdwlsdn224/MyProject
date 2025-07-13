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

    # 1) 테스트넷(또는 실제넷) 연결 시도
    client_async = None
    while client_async is None:
        try:
            # 테스트넷 URL을 명시적으로 지정
            client_async = await AsyncClient.create(
                API_KEY,
                API_SECRET,
                base_url="https://testnet.binance.vision"
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
    # 로컬에서 테스트할 때만 실행
    asyncio.run(run_bot_loop())
