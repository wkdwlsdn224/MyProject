from typing import Dict, Any
import pandas as pd

def get_signal(
    symbol: str,
    price: float,
    config: Dict[str, Any]
) -> bool:
    """
    심볼별 가격·모드·min_score를 보고 진입 신호를 반환
    """
    mode_cfg = config[symbol]
    threshold = mode_cfg["min_score"] * {
        "aggressive": 1.02,
        "neutral":    1.05,
        "conservative": 1.08
    }[mode_cfg["mode"]]
    return price > threshold

def simulate_best_strategies(
    history: pd.DataFrame,
    recommended_modes: Dict[str, str]
) -> pd.Series:
    """
    과거 거래 로그(history)에 recommended_modes를 매핑해
    모드별 평균 PnL 계산
    """
    df = history.copy()
    df["Recommended"] = df["Symbol"].map(recommended_modes)
    return df.groupby("Recommended")["PnL (%)"].mean()
