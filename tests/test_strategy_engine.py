import pandas as pd
from strategy_engine import get_signal, simulate_best_strategies

def test_get_signal():
    cfg = {"XYZ": {"min_score": 100, "mode": "aggressive"}}
    assert get_signal("XYZ", 105, cfg) is True
    assert get_signal("XYZ", 101, cfg) is False

def test_simulate_best_strategies():
    data = pd.DataFrame({
        "Symbol": ["A","A","B","B"],
        "PnL (%)": [1.0, 2.0, -0.5, 0.5]
    })
    rec = {"A": "m1", "B": "m2"}
    res = simulate_best_strategies(data, rec)
    assert res["m1"] == 1.5
    assert res["m2"] == 0.0
