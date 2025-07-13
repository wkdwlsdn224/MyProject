# bot.py

import asyncio
import logging

from binance import AsyncClient
from config import API_KEY, API_SECRET
from trade_executor import your_trading_iteration

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
            client_async = await AsyncClient.create(
                API_KEY,
                API_SECRET,
                testnet=True,                                   # <-- 쉼표 추가
                session_params={"trust_env": False},             # <-- 딕셔너리 닫는 괄호 추가
            )
            logging.info("[bot] Binance 테스트넷 연결 성공")
        except Exception as e:
            logging.warning(f"[bot] Binance 테스트넷 연결 실패, 30초 뒤 재시도합니다: {e}")
            await asyncio.sleep(30)

    # … (초기화 코드)

    while True:
        try:
            await your_trading_iteration(client_async)
        except Exception as e:
            logging.error(f"[bot] 루프 중 오류 발생, 계속 실행합니다: {e}")
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run_bot_loop())
