import csv, requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, EMOJI_MAP

def log_trade(fname, symbol, mode, lev, et, ep, xt, xp, pnl):
    with open(fname,"a",newline="") as f:
        csv.writer(f).writerow([symbol,mode,lev,et,f"{ep:.3f}",xt,f"{xp:.3f}",f"{pnl:.2f}%"])

def log_system(fname, msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(fname,"a",encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url,data={"chat_id":TELEGRAM_CHAT_ID,"text":msg})
    except:
        log_system("bot_log.txt","❌ Telegram 전송 실패")

def send_position_update(symbol, side, price, pnl=None):
    emo  = EMOJI_MAP.get(symbol,"")
    text = f"{emo} {symbol} {side} @ {price:.3f}"
    if pnl is not None:
        text += f"   결과: {pnl:.2f}%"
    send_telegram(text)
