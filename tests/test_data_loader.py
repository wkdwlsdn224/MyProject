import pandas as pd
from data_loader import load_trade_log

def test_load_trade_log(tmp_path):
    file = tmp_path / "log.csv"
    file.write_text("Symbol,PnL (%)\nA,1.0\nB,2.0\n")
    df = load_trade_log(str(file))
    assert list(df["PnL (%)"]) == [1.0, 2.0]
