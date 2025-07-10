import pandas as pd

def generate_trade_report(log_file="ultimate_trade_log.csv"):
    df = pd.read_csv(log_file)
    df["PnL (%)"] = df["PnL (%)"].astype(float)

    if df.empty:
        return "📋 전략 리포트: 거래 내역이 없습니다."

    win_rate = len(df[df["PnL (%)"] > 0]) / len(df) * 100
    avg_pnl = df["PnL (%)"].mean()
    total_pnl = df["PnL (%)"].sum()

    report = f"🎯 Supreme Bot 전략 리포트\n"
    report += f"- 총 거래 수: {len(df)}회\n"
    report += f"- 승률: {win_rate:.1f}%\n"
    report += f"- 평균 수익률: {avg_pnl:.2f}%\n"
    report += f"- 누적 수익률: {total_pnl:.2f}%"
    return report

def generate_trade_report(log_file="ultimate_trade_log.csv"):
    df = pd.read_csv(log_file)
    df["PnL"] = df["PnL"].astype(float)

    total_trades = len(df)
    wins = df[df["PnL"] > 0]
    losses = df[df["PnL"] < 0]

    win_rate = len(wins) / total_trades * 100 if total_trades else 0
    avg_win = wins["PnL"].mean() if not wins.empty else 0
    avg_loss = losses["PnL"].mean() if not losses.empty else 0
    net_pnl = df["PnL"].sum()
    best_trade = df.loc[df["PnL"].idxmax()] if not df.empty else None
    worst_trade = df.loc[df["PnL"].idxmin()] if not df.empty else None

    print("📊 Supreme Bot 트레이딩 요약 리포트")
    print(f"총 트레이딩: {total_trades}회")
    print(f"승률: {win_rate:.2f}%")
    print(f"평균 수익률 (승): {avg_win:.2f}%")
    print(f"평균 손실률: {avg_loss:.2f}%")
    print(f"총 누적 수익률: {net_pnl:.2f}%")

    if best_trade is not None:
        print(f"🔥 최대 수익: {best_trade['Symbol']} +{best_trade['PnL']}% @ {best_trade['Exit']}")
    if worst_trade is not None:
        print(f"🧊 최대 손실: {worst_trade['Symbol']} {worst_trade['PnL']}% @ {worst_trade['Exit']}")
