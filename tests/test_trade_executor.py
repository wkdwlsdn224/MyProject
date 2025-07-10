import pytest
from trade_executor import TradeExecutor

class DummyClient:
    def order_market_buy(self, symbol, quantity):
        return {"symbol": symbol, "qty": quantity}

def test_buy_market_success(monkeypatch):
    exec = TradeExecutor("key","sec")
    exec.client = DummyClient()
    res = exec.buy_market("ABC", 0.1)
    assert res["symbol"] == "ABC"
    assert res["qty"] == 0.1
