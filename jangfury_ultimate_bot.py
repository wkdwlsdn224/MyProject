import os
from dotenv import load_dotenv

load_dotenv()

# 1) 환경변수
API_KEY         = os.getenv("BINANCE_API_KEY")
API_SECRET      = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID= os.getenv("TELEGRAM_CHAT_ID")

# 필수 환경변수 체크
for name, val in {
    "BINANCE_API_KEY": API_KEY,
    "BINANCE_API_SECRET": API_SECRET,
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID
}.items():
    if not val:
        raise EnvironmentError(f"Missing env var: {name}")

# 2) 신뢰 심볼 리스트
RELIABLE_SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT","DOGEUSDT",
    "XRPUSDT","LTCUSDT","MATICUSDT","ADAUSDT","DOTUSDT","FTMUSDT",
    "INJUSDT","ARBUSDT","LINKUSDT","OPUSDT","NEARUSDT","ATOMUSDT",
    "UNIUSDT","SANDUSDT","LDOUSDT","RNDRUSDT"
]

# 3) 심볼별 기본 레버리지
SYMBOL_LEVERAGE = {
    s: 10 for s in RELIABLE_SYMBOLS
}

# 4) 심볼별 이모지 매핑 (Telegram용)
EMOJI_MAP = {
    "BTCUSDT":"🟡","ETHUSDT":"⚪️","BNBUSDT":"🟠","SOLUSDT":"🔵",
    "AVAXUSDT":"💧","DOGEUSDT":"🐶","XRPUSDT":"❌","LTCUSDT":"🔗",
    "MATICUSDT":"🐉","ADAUSDT":"🔺","DOTUSDT":"⚫️","FTMUSDT":"🌪",
    "INJUSDT":"✈️","ARBUSDT":"🌲","LINKUSDT":"🔗","OPUSDT":"🚪",
    "NEARUSDT":"🌐","ATOMUSDT":"☢️","UNIUSDT":"🦄","SANDUSDT":"🏖",
    "LDOUSDT":"⚰️","RNDRUSDT":"🎨"
}

from config import RELIABLE_SYMBOLS

async def get_reliable_symbols(client):
    """
    Binance Futures에서 등록된 전체 심볼 중
    신뢰 리스트에 포함된 것만 반환
    """
    info = await client.futures_exchange_info()
    all_symbols = [s["symbol"] for s in info["symbols"]]
    return [s for s in all_symbols if s in RELIABLE_SYMBOLS]

from config import SYMBOL_LEVERAGE

async def get_usdt_balance(client):
    """
    Futures 계정의 USDT 잔고 조회
    """
    bals = await client.futures_account_balance()
    for item in bals:
        if item["asset"] == "USDT":
            return float(item["balance"])
    return 0.0

async def calculate_quantity(client, symbol, usdt_balance):
    """
    가격·정밀도·레버리지·최소 Notional을 반영해
    진입 수량을 자동 계산
    """
    lev   = SYMBOL_LEVERAGE.get(symbol, 10)
    price = float((await client.futures_mark_price(symbol=symbol))["markPrice"])
    info  = await client.get_symbol_info(symbol)
    precision = int(info["quantityPrecision"])
    amount    = usdt_balance * 0.9 * lev
    qty       = max(amount / price, 1 / price)
    return round(qty, precision)

from ta import momentum, trend, volatility

def enrich(df):
    """
    DataFrame에 RSI, MACD 히스토그램, Bollinger Band, EMA20/50 컬럼 추가
    """
    df["rsi"]       = momentum.rsi(df["close"], window=14)
    macd            = trend.MACD(df["close"])
    df["macd_hist"] = macd.macd_diff()
    bb              = volatility.BollingerBands(df["close"])
    df["bb_hi"]     = bb.bollinger_hband()
    df["bb_lo"]     = bb.bollinger_lband()
    df["ema20"]     = trend.ema_indicator(df["close"], window=20)
    df["ema50"]     = trend.ema_indicator(df["close"], window=50)
    return df

def check_flags(df, long=True):
    """
    진입 조건 5가지 플래그
    """
    return [
        (df["rsi"].iloc[-1] < 30) if long else (df["rsi"].iloc[-1] > 70),
        (df["macd_hist"].iloc[-1] > 0) if long else (df["macd_hist"].iloc[-1] < 0),
        (df["close"].iloc[-1] < df["bb_lo"].iloc[-1]) if long
            else (df["close"].iloc[-1] > df["bb_hi"].iloc[-1]),
        (df["ema20"].iloc[-1] > df["ema50"].iloc[-1]) if long
            else (df["ema20"].iloc[-1] < df["ema50"].iloc[-1]),
        (df["close"].iloc[-3:].is_monotonic_increasing) if long
            else (df["close"].iloc[-3:].is_monotonic_decreasing)
    ]

import csv, requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, EMOJI_MAP

def log_trade(fname, symbol, mode, leverage, et, ep, xt, xp, pnl):
    """
    거래 내역을 CSV에 기록
    """
    with open(fname, "a", newline="") as f:
        csv.writer(f).writerow([
            symbol, mode, leverage,
            et, f"{ep:.3f}",
            xt, f"{xp:.3f}", f"{pnl:.2f}%"
        ])

def log_system(fname, msg):
    """
    시스템 로그에 기록 + 콘솔 출력
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(fname, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def send_telegram(msg):
    """
    Telegram 단순 텍스트 전송
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        log_system("bot_log.txt","❌ Telegram 전송 실패")

def send_position_update(symbol, side, price, pnl=None):
    """
    포지션 알림: 이모지·PnL 포함
    """
    emoji = EMOJI_MAP.get(symbol, "")
    text  = f"{emoji} {symbol} {side} @ {price:.3f}"
    if pnl is not None:
        text += f"  결과: {pnl:.2f}%"
    send_telegram(text)

import pandas as pd

def load_trades(file="ultimate_trade_log.csv"):
    df = pd.read_csv(file)
    df["PnL (%)"] = df["PnL (%)"].str.rstrip("%").astype(float)
    return df

def summary(df):
    total    = len(df)
    wins     = len(df[df["PnL (%)"] > 0])
    losses   = total - wins
    win_rate = wins/total*100 if total else 0
    avg_pnl  = df["PnL (%)"].mean() if total else 0
    total_pnl= df["PnL (%)"].sum() if total else 0
    return {
        "total_trades": total,
        "win_rate": win_rate,
        "avg_pnl": avg_pnl,
        "total_pnl": total_pnl
    }

def report(file="ultimate_trade_log.csv"):
    """
    터미널에 성과 요약 리포트 출력
    """
    df = load_trades(file)
    s  = summary(df)
    print("📝 Trading Performance Summary")
    print(f"Total Trades: {s['total_trades']}")
    print(f"Win Rate: {s['win_rate']:.2f}%")
    print(f"Average PnL: {s['avg_pnl']:.2f}%")
    print(f"Total PnL: {s['total_pnl']:.2f}%")

import asyncio, os, time
import pandas as pd
from datetime import datetime
from binance import AsyncClient, BinanceSocketManager
from config import API_KEY, API_SECRET, RELIABLE_SYMBOLS, SYMBOL_LEVERAGE
from filters import get_reliable_symbols
from quantity import get_usdt_balance, calculate_quantity
from strategy import enrich, check_flags
from logging import (
    log_trade, log_system,
    send_position_update, send_telegram
)

TRADE_LOG  = "ultimate_trade_log.csv"
SYSTEM_LOG = "bot_log.txt"
FEE_PCT    = 0.08

# 초기 CSV 헤더
if not os.path.exists(TRADE_LOG):
    with open(TRADE_LOG, "w", newline="") as f:
        import csv
        csv.writer(f).writerow([
            "Symbol","Mode","Leverage",
            "Entry Time","Entry Price",
            "Exit Time","Exit Price","PnL (%)"
        ])

async def watch(client, symbol):
    lev = SYMBOL_LEVERAGE.get(symbol, 10)
    try:
        await client.futures_change_leverage(symbol=symbol, leverage=lev)
        send_telegram(f"🔍 감시 시작: {symbol} x{lev}배")
        log_system(SYSTEM_LOG, f"감시 시작 {symbol}")
    except Exception as e:
        log_system(SYSTEM_LOG, f"레버리지 설정 실패 {symbol}: {e}")
        return

    entry_price = None
    entry_time  = None
    position    = None
    ohlcv_1m    = []

    bm = BinanceSocketManager(client)
    async with bm.kline_socket(symbol=symbol, interval="1m") as stream:
        while True:
            msg = await stream.recv()
            k   = msg["k"]
            if not k["x"]: continue

            close = float(k["c"])
            ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ohlcv_1m.append(close)
            if len(ohlcv_1m) < 50: continue

            df1  = enrich(pd.DataFrame(ohlcv_1m[-100:], columns=["close"]))
            raw15= await client.futures_klines(symbol=symbol, interval="15m", limit=100)
            df15 = enrich(pd.DataFrame([float(x[4]) for x in raw15], columns=["close"]))

            long_flags  = check_flags(df1, True)  + check_flags(df15, True)
            short_flags = check_flags(df1, False) + check_flags(df15, False)

            # 진입
            if entry_price is None:
                direction = "NONE"
                if any(long_flags):   direction = "LONG"
                elif any(short_flags):direction = "SHORT"

                if direction != "NONE":
                    usdt= await get_usdt_balance(client)
                    qty = await calculate_quantity(client, symbol, usdt)
                    if qty is None or qty <= 0:
                        log_system(SYSTEM_LOG, f"수량 계산 실패 {symbol}")
                        continue

                    side = "BUY" if direction=="LONG" else "SELL"
                    try:
                        order = await client.futures_create_order(
                            symbol=symbol, side=side,
                            type="MARKET", quantity=qty
                        )
                        entry_price = float(order.get("avgFillPrice", close))
                        entry_time  = ts
                        position    = direction
                        log_trade(
                            TRADE_LOG, symbol, direction, lev,
                            entry_time, entry_price, "", 0
                        )
                        send_position_update(symbol, direction, entry_price)
                        log_system(SYSTEM_LOG, f"진입 성공 {symbol} @ {entry_price:.3f}")
                    except Exception as e:
                        send_telegram(f"❌ 진입 실패 [{symbol}]: {e}")
                        log_system(SYSTEM_LOG, f"진입 실패 {symbol}: {e}")

            # 청산
            else:
                pnl_ratio = (
                    (close-entry_price)/entry_price
                    if position=="LONG"
                    else (entry_price-close)/entry_price
                )
                real_pnl = pnl_ratio - (FEE_PCT/100)
                pnl_pct   = real_pnl * 100

                if real_pnl >= 0.15 or real_pnl <= -0.03:
                    exit_side = "SELL" if position=="LONG" else "BUY"
                    try:
                        await client.futures_create_order(
                            symbol=symbol, side=exit_side,
                            type="MARKET", quantity=qty
                        )
                        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_trade(
                            TRADE_LOG, symbol, position, lev,
                            entry_time, entry_price,
                            exit_time, close, pnl_pct
                        )
                        tag = "🎯 익절" if pnl_pct>0 else "⚠️ 손절"
                        send_position_update(symbol, tag, close, pnl_pct)
                        log_system(SYSTEM_LOG, f"{tag} {symbol} @ {close:.3f} | PnL {pnl_pct:.2f}%")
                    except Exception as e:
                        send_telegram(f"❌ 청산 실패 [{symbol}]: {e}")
                        log_system(SYSTEM_LOG, f"청산 실패 {symbol}: {e}")
                    finally:
                        entry_price = None
                        position    = None

async def main():
    client = await AsyncClient.create(API_KEY, API_SECRET)
    send_telegram("🚀 Supreme Edition Bot 시작")
    log_system(SYSTEM_LOG, "봇 시동 완료")
    symbols = await get_reliable_symbols(client)
    tasks   = [asyncio.create_task(watch(client, s)) for s in symbols]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
            break
        except Exception as e:
            send_telegram(f"🌀 봇 중단 — 재시작:\n{e}")
            log_system(SYSTEM_LOG, f"재시작 오류: {e}")
            time.sleep(10)
