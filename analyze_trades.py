import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import requests

def load_data(csv_path="ultimate_trade_log.csv"):
    try:
        df = pd.read_csv(csv_path)
        df["Entry Time"] = pd.to_datetime(df["Entry Time"])
        df["Exit Time"]  = pd.to_datetime(df["Exit Time"])
        df["Duration"]   = (df["Exit Time"] - df["Entry Time"]).dt.total_seconds() / 60
        return df
    except Exception as e:
        print(f"❌ CSV 불러오기 실패: {e}")
        return None

def summarize(df):
    total    = len(df)
    wins     = df[df["PnL (%)"] > 0]
    losses   = df[df["PnL (%)"] <= 0]
    winrate  = (len(wins) / total) * 100 if total > 0 else 0
    cum_pnl  = df["PnL (%)"].sum()
    avg_pnl  = df["PnL (%)"].mean()
    max_win  = df["PnL (%)"].max()
    max_loss = df["PnL (%)"].min()

    summary = f"""📊 Supreme Bot 성과 요약
───────────────
총 거래 수     : {total}
승률          : {winrate:.2f}%
누적 수익률   : {cum_pnl:.2f}%
평균 손익      : {avg_pnl:.2f}%
최대 수익      : {max_win:.2f}%
최대 손실      : {max_loss:.2f}%"""
    print(summary)
    return summary

def visualize(df):
    plt.figure(figsize=(10,6))
    sns.histplot(df["PnL (%)"], bins=40, kde=True, color="skyblue")
    plt.axvline(0, color="gray", linestyle="--")
    plt.title("PnL 분포 히스토그램")
    plt.xlabel("손익 퍼센트 (%)")
    plt.ylabel("거래 수")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("pnl_histogram.png")
    print("📈 히스토그램 저장 완료")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("✅ Telegram 전송 완료")
        else:
            print(f"❌ Telegram 실패: {res.text}")
    except Exception as e:
        print(f"❌ Telegram 예외: {e}")

if __name__ == "__main__":
    df = load_data()
    if df is not None and not df.empty:
        msg = summarize(df)
        visualize(df)
        send_telegram(msg)
    else:
        print("⚠️ 분석할 거래 데이터가 없습니다.")
