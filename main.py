# main.py

import asyncio
import uvicorn
from health import app as health_app
from bot import run_bot_loop

async def start_api():
    config = uvicorn.Config(health_app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    while True:
        try:
            await run_bot_loop()
        except Exception as e:
            print(f"[main] bot 에서 오류 발생, 30초 뒤 재시작: {e}")
        await asyncio.sleep(30)

async def main():
    # 헬스 서버는 절대 종료되지 않도록 하고,
    # bot 은 내부에서 재시도 로직이 있으면 여기서 단순 실행만
    await asyncio.gather(
        start_api(),
        start_bot(),
    )

if __name__ == "__main__":
    asyncio.run(main())
