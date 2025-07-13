# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로드

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# 전략 관련 설정
STRATEGY_MODE = os.getenv("STRATEGY_MODE", "neutral")
MIN_STRATEGY_SCORE = int(os.getenv("MIN_STRATEGY_SCORE", "2"))

# 신뢰 심볼 리스트 (콤마로 구분된 문자열을 파싱해서 리스트로 만듭니다)
_raw = os.getenv("RELIABLE_SYMBOLS", "")
if _raw:
    RELIABLE_SYMBOLS = [s.strip() for s in _raw.split(",") if s.strip()]
else:
    RELIABLE_SYMBOLS = []

# 기타 설정 예시
ENV = os.getenv("ENV", "development")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")

# (필요한 다른 설정들도 여기에 추가)
