# 📦 config.py — Supreme Bot 전략 설정 파일

# 🎯 기본 수익률 / 손절률
DEFAULT_TAKE_PROFIT = 0.12    # 💰 수익 목표 +15%
DEFAULT_STOP_LOSS   = -0.08   # 🛑 손절 기준 -10%

# 🧠 봇이 자동으로 조건을 바꿔도 되도록 허용
ALLOW_DYNAMIC_RATIO = True

# 📈 전략 조건 기준 점수
MIN_STRATEGY_SCORE = 2  # MA, RSI, MACD 등 최소 2개 전략 만족 시 진입

# 🕰️ 시간봉 구성
ACTIVE_INTERVALS = ["3m", "15m", "1h", "4h"]

STRATEGY_MODE = "auto"  # "auto", "scalp", "swing"
