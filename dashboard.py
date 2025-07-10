import json
import logging
from utils import exception_notifier

@exception_notifier
def show_analysis():
    # 기존 분석 탭 코드...

@exception_notifier
def trade_interface():
    # 기존 주문 탭 코드...

show_analysis()
trade_interface()

# 파일 로드
def load_json(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"파일을 찾을 수 없습니다: {path}", exc_info=True)
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON 파싱 오류: {path} → {e}", exc_info=True)
        raise

# 파일 저장
def save_json(path: str, data: dict):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"JSON 저장 실패: {path} → {e}", exc_info=True)
        raise

import streamlit as st
import yaml
import streamlit_authenticator as stauth

# ① credentials.yaml 불러오기
with open("credentials.yaml") as f:
    cred_cfg = yaml.safe_load(f)

# ② Authenticator 인스턴스 생성
authenticator = stauth.Authenticate(
    cred_cfg["credentials"],
    cred_cfg["cookie"]["name"],
    cred_cfg["cookie"]["key"],
    cred_cfg["cookie"]["expiry_days"]
)

# ③ 폼 제목은 직접 달아줍니다
st.title("Supreme Bot 로그인")

# ④ login() 호출 – 반드시 keyword 방식으로
login_result = authenticator.login(
    location="main",
    fields={"username": "사용자 ID", "password": "비밀번호"},
    clear_on_submit=False,
    key="login_form"
)

# ⑤ 폼이 제출되지 않은 초기 렌더라면 None → 멈추기
if login_result is None:
    # 로그인 폼만 보여주고 나머지 코드는 실행하지 않습니다
    st.stop()

# ⑥ 이제 안전하게 튜플 언패킹
name, status, username = login_result

# ⑦ 로그인 성공/실패 처리
if status:
    st.success(f"환영합니다, {name}님!")
elif status is False:
    st.error("아이디 또는 비밀번호가 올바르지 않습니다")
    st.stop()
else:  # status is None
    st.warning("로그인을 위해 아이디/비밀번호를 입력해주세요")
    st.stop()

# ─── 로그인 완료 후 대시보드 나머지 코드 ───

# ── 로그인 성공 후 대시보드 코드 계속 ──

st.title("로그인")

# dashboard.py 상단
from dotenv import load_dotenv
import os

load_dotenv()   # .env 파일 읽어들임

import streamlit as st
from binance.client import Client

api_key    = st.secrets["binance"]["API_KEY"]
api_secret = st.secrets["binance"]["SECRET_KEY"]
client     = Client(api_key, api_secret)

class SecretFilter(logging.Filter):
    def __init__(self, secrets):
        super().__init__()
        self.patterns = [re.escape(s) for s in secrets if s]

    def filter(self, record):
        msg = record.getMessage()
        for p in self.patterns:
            msg = re.sub(p, "[REDACTED]", msg)
        record.msg = msg
        return True

# 기존 코드 계속…

import os
import json
import logging
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from apscheduler.schedulers.background import BackgroundScheduler
from binance.client import Client

from utils import (
    send_telegram,
    get_current_positions,
    get_current_price
)
from report_generator import generate_trade_report
from strategy_optimizer import optimize_strategy_config
from strategy_recommender import recommend_best_strategy
from strategy_tracker import compare_strategy_configs
from strategy_predictor import predict_mode

# ───────────────────────────────────────────────────────────
# 1) 초기 설정
# ───────────────────────────────────────────────────────────
st.set_page_config(page_title="Supreme Bot Dashboard", layout="wide")
st.title("📊 Supreme Bot 전략 대시보드")

# 로깅 설정
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# 기본 로깅 설정
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# 환경변수 또는 st.secrets에서 불러온 비밀키
secret_list = [
    os.getenv("BINANCE_API_KEY", ""),
    os.getenv("BINANCE_SECRET_KEY", ""),
    os.getenv("TELEGRAM_TOKEN", "")
]

# 필터 추가
logging.getLogger().addFilter(SecretFilter(secret_list))

# Binance API 클라이언트
client = Client(
    os.getenv("BINANCE_API_KEY"),
    os.getenv("BINANCE_SECRET_KEY")
)

# 거래 기록 불러오기
df = pd.read_csv("ultimate_trade_log.csv")
df["PnL (%)"] = df["PnL (%)"].astype(float)

# 전략 설정 불러오기
with open("strategy_config.json") as f:
    strategy_config = json.load(f)

# 스케줄러 (리포트용)
scheduler = BackgroundScheduler()


# ───────────────────────────────────────────────────────────
# 2) 사이드바 설정
# ───────────────────────────────────────────────────────────
def sidebar_settings():
    st.sidebar.header("⚙️ 전략 파라미터 설정")
    sym0 = next(iter(strategy_config))
    default = strategy_config[sym0]
    
    min_score = st.sidebar.slider(
        "최소 전략 점수(min_score)",
        min_value=0.0, max_value=10.0, step=0.1,
        value=float(default.get("min_score", 1.0))
    )
    tp = st.sidebar.slider(
        "목표 수익률(%)",
        min_value=0.0, max_value=20.0, step=0.5,
        value=default.get("tp", 3.0)
    )
    sl = st.sidebar.slider(
        "손실 제한(%)",
        min_value=-20.0, max_value=0.0, step=0.5,
        value=default.get("sl", -5.0)
    )
    if st.sidebar.button("✅ 설정 저장"):
        for sym in strategy_config:
            strategy_config[sym]["min_score"] = min_score
            strategy_config[sym]["tp"] = tp
            strategy_config[sym]["sl"] = sl
        with open("strategy_config.json", "w") as f:
            json.dump(strategy_config, f, indent=2)
        st.sidebar.success("전략 파라미터 저장 완료!")

sidebar_settings()


# ───────────────────────────────────────────────────────────
# 3) 기능별 UI 함수 정의
# ───────────────────────────────────────────────────────────
def show_analysis():
    st.subheader("🔥 전략 성과 히트맵")
    heatmap = df.pivot_table(
        index="Symbol", columns="Mode", values="PnL (%)", aggfunc="mean"
    )
    fig, ax = plt.subplots()
    sns.heatmap(heatmap, annot=True, fmt=".2f", cmap="RdYlGn", ax=ax)
    st.pyplot(fig)

    st.subheader("📋 전략 성과 리포트")
    report = generate_trade_report()
    st.code(report, language="markdown")

    st.subheader("🧠 전략 추천 탐색기")
    recommended = recommend_best_strategy(df)
    st.json(recommended)

    st.subheader("🔄 전략 모드 변경 이력")
    changes = compare_strategy_configs("strategy_config_old.json", "strategy_config.json")
    st.json(changes)

    st.subheader("📈 전략 변화 시점 그래프 (BTCUSDT)")
    btc = df[df["Symbol"] == "BTCUSDT"]
    fig, ax = plt.subplots()
    ax.plot(btc["Entry Time"], btc["PnL (%)"], marker="o")
    for i, mode in enumerate(btc["Mode"]):
        ax.annotate(mode, (btc["Entry Time"].iloc[i], btc["PnL (%)"].iloc[i]))
    ax.set_xlabel("시간")
    ax.set_ylabel("PnL (%)")
    st.pyplot(fig)


def trade_interface():
    st.subheader("🚀 실거래 진입 인터페이스")
    symbol = st.selectbox("심볼 선택", df["Symbol"].unique())
    amount = st.number_input("진입 수량", min_value=0.001, value=0.1)
    if st.button("📥 포지션 진입"):
        price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        client.order_market_buy(symbol=symbol, quantity=amount)
        send_telegram(f"✅ [{symbol}] 진입 - 수량 {amount} @ {price}")
        st.success(f"{symbol} 주문 완료")


def show_positions_and_autoclose():
    st.subheader("📊 실시간 포지션 모니터링 & 자동 청산")
    positions = get_current_positions()
    tp, tl = 3.0, -5.0

    for p in positions:
        pnl = (p["current_price"] - p["entry_price"]) / p["entry_price"] * 100
        st.markdown(f"**{p['symbol']}** | 수량: {p['amount']} | PnL: {pnl:.2f}%")
        st.metric("수익률 (%)", f"{pnl:.2f}%")

        if pnl < tl:
            send_telegram(f"⚠️ {p['symbol']} 손실 {pnl:.2f}%")
            st.error("손실 위험")

        if pnl >= tp or pnl <= tl:
            client.order_market_sell(symbol=p["symbol"], quantity=p["amount"])
            send_telegram(f"💼 자동 청산: {p['symbol']} → PnL {pnl:.2f}%")
            st.success("청산 완료")


def show_predictor():
    st.subheader("🔮 ML 기반 전략 모드 예측")
    symbol = st.selectbox("예측 심볼", df["Symbol"].unique())
    sample = pd.DataFrame({
        "Leverage": [3], "PnL (%)": [1.5], "Symbol": [symbol]
    })
    mode = predict_mode(sample)[0]
    st.success(f"추천 전략 모드: {mode}")


def show_backtest_experiments():
    st.subheader("🧪 다중 전략 백테스트")
    strategies = ["SMA", "EMA", "RSI", "AI", "Trend"]
    def backtest(symbol, strat):
        return df[(df["Symbol"] == symbol) & (df["Mode"] == strat)]["PnL (%)"].mean()
    results = {s: backtest("BTCUSDT", s) for s in strategies}
    st.bar_chart(pd.Series(results))
    best = max(results, key=results.get)
    st.success(f"최고 전략: {best} → {results[best]:.2f}% 평균 PnL")


def show_signal_generator():
    st.subheader("📡 실시간 전략 신호 발생기")
    symbol = st.selectbox("신호 심볼", df["Symbol"].unique())
    price = get_current_price(symbol)
    cfg = strategy_config[symbol]
    factor = {"aggressive":1.02, "neutral":1.05, "conservative":1.08}[cfg["mode"]]
    signal = price > cfg["min_score"] * factor
    st.write(f"현재가: {price:.2f} | 진입 신호: {signal}")


def show_feedback_loop():
    st.subheader("🔄 전략 피드백 루프 평가")
    rec = recommend_best_strategy(df)
    out = {}
    for sym in df["Symbol"].unique():
        sub = df[df["Symbol"] == sym]
        cur = strategy_config[sym]["mode"]
        actual = sub[sub["Mode"] == cur]["PnL (%)"].mean()
        rp = sub[sub["Mode"] == rec[sym]]["PnL (%)"].mean()
        out[sym] = {
            "current": cur,
            "current_pnl": actual,
            "recommended": rec[sym],
            "reco_pnl": rp
        }
    st.json(out)


def send_scheduled_report():
    report = generate_trade_report()
    send_telegram(f"📅 정기 리포트\n\n{report}")


def show_report_scheduler():
    st.subheader("🗓️ 리포트 스케줄러")
    use = st.checkbox("정기 발송 활성화")
    cron = st.text_input("Cron 표현식", "0 9 * * *",
                         help="분 시 일 월 요일 (예: 매일 09:00 → 0 9 * * *)")
    jobs = scheduler.get_jobs()
    if use and not jobs:
        m, h, d, mo, wd = cron.split()
        scheduler.add_job(
            send_scheduled_report, trigger="cron",
            minute=m, hour=h, day=d, month=mo, day_of_week=wd,
            id="daily_report"
        )
        scheduler.start()
        st.success("스케줄러 등록 완료")
    if not use and jobs:
        scheduler.remove_job("daily_report")
        st.warning("스케줄러 해제됨")
    if st.button("📤 즉시 리포트 발송"):
        send_scheduled_report()
        st.success("즉시 발송 완료")


def show_logging():
    st.subheader("📝 로그 뷰어 & 모니터링")
    if os.path.exists("app.log"):
        with open("app.log") as f:
            lines = f.readlines()[-100:]
        st.text_area("최근 로그", "".join(lines), height=300)
        orders = sum(1 for l in lines if "포지션 진입" in l)
        exits  = sum(1 for l in lines if "자동 청산" in l)
        st.metric("총 진입 주문", orders)
        st.metric("총 자동 청산", exits)
    else:
        st.info("로그 파일이 없습니다.")


def show_ml_pipeline():
    st.subheader("🤖 ML 파이프라인 관리")
    col1, col2 = st.columns(2)
    import ml_pipeline
    with col1:
        if st.button("🔄 모델 재학습"):
            with st.spinner("모델 학습 중..."):
                ml_pipeline.train_model()
            st.success("재학습 완료")
    with col2:
        info = ml_pipeline.get_model_info()
        st.metric("모델 버전", info["version"])
        st.metric("학습일", info["last_trained"])
        st.metric("Val AUC", f"{info['val_auc']:.3f}")


# ───────────────────────────────────────────────────────────
# 4) 탭 구성
# ───────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 분석",
    "💼 실거래",
    "🔔 감시/청산",
    "🔮 예측",
    "🧪 백테스트",
    "📡 신호",
    "🔄 피드백",
    "🗓️ 스케줄",
    "📝 로그",
    "🤖 ML"
])

with tabs[0]: show_analysis()
with tabs[1]: trade_interface()
with tabs[2]: show_positions_and_autoclose()
with tabs[3]: show_predictor()
with tabs[4]: show_backtest_experiments()
with tabs[5]: show_signal_generator()
with tabs[6]: show_feedback_loop()
with tabs[7]: show_report_scheduler()
with tabs[8]: show_logging()
with tabs[9]: show_ml_pipeline()
