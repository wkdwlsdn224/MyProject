import json

with open("strategy_config.json") as f:
    strategy_config = json.load(f)

for symbol in symbols:
    config = strategy_config.get(symbol, {})
    mode = config.get("mode", "neutral")
    min_score = config.get("min_score", MIN_STRATEGY_SCORE)

    score = get_strategy_score(df)
    if score < min_score:
        log_event(f"{symbol}: 전략 점수 부족 ({score} < {min_score}) → 진입 보류")
        continue

from your_candle_module import load_candle_data

# 📦 main.py — Supreme Bot 실행 구조 (실전형 예시)
import asyncio
import numpy as np
from config import DEFAULT_TAKE_PROFIT, DEFAULT_STOP_LOSS, ALLOW_DYNAMIC_RATIO, MIN_STRATEGY_SCORE
from strategy import get_strategy_score
from predict import predict_future
from risk import compute_leverage
from utils import send_telegram, log_event, record_trade

from binance import AsyncClient  # Binance API 사용
from your_candle_module import load_candle_data  # 직접 만든 데이터 로더 모듈

# ✅ TP/SL 동적 계산
def get_dynamic_thresholds(volatility):
    if not ALLOW_DYNAMIC_RATIO:
        return DEFAULT_TAKE_PROFIT, DEFAULT_STOP_LOSS

    if volatility > 100:
        return 0.10, -0.15
    elif volatility > 50:
        return 0.13, -0.12
    else:
        return 0.17, -0.08

# 🔁 전체 루프
async def run_bot():
    client = await AsyncClient.create()
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]  # 감시할 심볼들
    positions = {}

    while True:
        for symbol in symbols:
            df = await load_candle_data(client, symbol, interval="1h", limit=100)
            if symbol not in positions:
                score = get_strategy_score(df)
                if score < MIN_STRATEGY_SCORE:
                    continue
                if not predict_future(symbol):
                    continue

                lev = await compute_leverage(symbol)
                await client.futures_change_leverage(symbol=symbol, leverage=lev)

                entry_price = df["close"].iloc[-1]
                positions[symbol] = entry_price
                send_telegram(f"🟢 진입: {symbol} @ {entry_price} (x{lev})")
                log_event(f"{symbol} 진입 @ {entry_price}, 점수={score}, 레버리지={lev}")
            else:
                entry_price = positions[symbol]
                current_price = df["close"].iloc[-1]
                pnl = (current_price - entry_price) / entry_price
                volatility = np.std(df["close"][-24:])
                tp, sl = get_dynamic_thresholds(volatility)

                if pnl >= tp or pnl <= sl:
                    send_telegram(f"🔴 청산: {symbol} @ {current_price} → PnL: {round(pnl*100,2)}%")
                    log_event(f"청산: {symbol}, 수익률={round(pnl*100,2)}%")
                    record_trade(symbol, "LONG", entry_price, current_price, pnl)
                    positions.pop(symbol)

        await asyncio.sleep(60)  # 1분마다 반복 감시

# ✅ 실행
if __name__ == "__main__":
    asyncio.run(run_bot())


# 📦 main.py — LSTM 예측 기능 통합 루틴
from predict_lstm import train_lstm, predict_future_lstm
from strategy import get_strategy_score
from config import MIN_STRATEGY_SCORE
from risk import compute_leverage
from utils import send_telegram, log_event, record_trade
from your_candle_module import load_candle_data

# LSTM 모델은 봇 시작 시 미리 학습
model = None
scaler = None

async def run_bot():
    global model, scaler

    client = await AsyncClient.create()
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    # 🧠 최초 1회 LSTM 학습 실행 (BTC 기준)
    df_train = await load_candle_data(client, "BTCUSDT", interval="1h", limit=500)
    df_train = df_train.reset_index(drop=True)  # 필요 시 인덱스 초기화
    model, scaler = train_lstm(df_train)

    while True:
        for symbol in symbols:
            df = await load_candle_data(client, symbol, interval="1h", limit=100)
            df = df.reset_index(drop=True)

            score = get_strategy_score(df)
            if score < MIN_STRATEGY_SCORE:
                continue

            is_up = predict_future_lstm(model, scaler, df)
            if not is_up:
                continue

            lev = await compute_leverage(symbol)
            await client.futures_change_leverage(symbol=symbol, leverage=lev)

            entry_price = df["close"].iloc[-1]
            send_telegram(f"🟢 진입: {symbol} @ {entry_price} (전략 {score}, LSTM 상승 예측)")
            log_event(f"진입: {symbol}, 가격={entry_price}, 레버리지={lev}")
            # 진입 후 포지션 열기 코드 추가

        await asyncio.sleep(60)

# === import 영역 ===
from strategy import get_strategy_score
from predict_lstm import train_lstm, predict_future_lstm, get_lstm_confidence
from market_state import classify_market
from risk import compute_leverage, get_dynamic_thresholds
from utils import send_telegram, log_event, record_trade
from your_candle_module import load_candle_data
from config import MIN_STRATEGY_SCORE

# === 봇 실행 ===
async def run_bot():
    client = await AsyncClient.create()
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    df_train = await load_candle_data(client, "BTCUSDT", "1h", 500)
    model, scaler = train_lstm(df_train)

    positions = {}

    while True:
        for symbol in symbols:
            df = await load_candle_data(client, symbol, "1h", 100)
            market = classify_market(df)

            # 전략 기준 상황별 조정
            if market == "bullish": strategy_threshold = MIN_STRATEGY_SCORE - 1
            elif market == "bearish": strategy_threshold = MIN_STRATEGY_SCORE + 1
            else: strategy_threshold = MIN_STRATEGY_SCORE

            score = get_strategy_score(df)
            if score < strategy_threshold:
                continue

            if not predict_future_lstm(model, scaler, df):
                continue

            lev = await compute_leverage(symbol)
            await client.futures_change_leverage(symbol=symbol, leverage=lev)

            entry_price = df["close"].iloc[-1]
            positions[symbol] = entry_price
            send_telegram(f"🟢 진입: {symbol} @ {entry_price}")
            log_event(f"{symbol} 진입 @ {entry_price}")

        # 청산 감시 루프
        for symbol, entry_price in positions.items():
            df = await load_candle_data(client, symbol, "1h", 100)
            current_price = df["close"].iloc[-1]
            pnl = (current_price - entry_price) / entry_price

            volatility = df["close"][-24:].std()
            tp, sl = get_dynamic_thresholds(volatility)

            ai_conf = get_lstm_confidence(model, scaler, df)
            tp *= 1 + (ai_conf - 0.5)
            sl *= 1 + (ai_conf - 0.5)

            if pnl >= tp or pnl <= sl:
                send_telegram(f"🔴 청산: {symbol} @ {current_price} → PnL {round(pnl*100,2)}%")
                log_event(f"{symbol} 청산 @ {current_price}")
                record_trade(symbol, "LONG", entry_price, current_price, pnl)
                positions.pop(symbol)

        await asyncio.sleep(60)

async def process_symbol(symbol, client):
    df = await load_candle_data(client, symbol, "1h", 100)
    market = classify_market(df)
    score = get_strategy_score(df)

    # 전략 모드 조정 (시간대 스케줄러)
    hour = datetime.utcnow().hour
    strategy_mode = "scalp" if hour < 16 else "swing"
    if strategy_mode == "scalp": score += 1

    # 자산 비중 판단
    if portfolio[symbol] < 0.05:
        log_event(f"{symbol}: 비중 낮아 진입 보류")
        return

    is_up = predict_future_lstm(model, scaler, df)
    if score >= MIN_STRATEGY_SCORE and is_up:
        entry_price = df["close"].iloc[-1]
        send_telegram(f"🟢 진입: {symbol} @ {entry_price}")

async def run_bot():
    client = await AsyncClient.create()
    symbols = list(portfolio.keys())

    tasks = [process_symbol(symbol, client) for symbol in symbols]
    await asyncio.gather(*tasks)

if STRATEGY_MODE == "auto":
    hour = datetime.utcnow().hour
    strategy_mode = "scalp" if hour < 16 else "swing"
elif STRATEGY_MODE == "scalp":
    strategy_mode = "scalp"
else:
    strategy_mode = "swing"

# 전략 튜닝
if strategy_mode == "scalp": score += 1

from performance import adjust_strategy_mode, load_log_df
from tracker import update_symbol_performance, get_symbol_performance

# ✅ 루프 시작 직전
log_df = load_log_df()
strategy_mode = adjust_strategy_mode(log_df)

if strategy_mode == "aggressive":
    strategy_threshold = MIN_STRATEGY_SCORE - 1
elif strategy_mode == "conservative":
    strategy_threshold = MIN_STRATEGY_SCORE + 1
else:
    strategy_threshold = MIN_STRATEGY_SCORE

# ✅ 진입 루틴 내부
performance = get_symbol_performance(symbol)
if performance["avg_pnl"] < 0:
    log_event(f"{symbol}: 최근 평균 수익률 낮아 진입 보류")
    continue
