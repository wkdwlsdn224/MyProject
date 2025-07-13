# portfolio.py

from typing import Dict

class Portfolio:
    """
    현재 포지션을 관리하는 간단한 포트폴리오 클래스입니다.
    심볼별로 진입 방향(“LONG”/“SHORT”)과 진입 가격을 기록하고 조회할 수 있습니다.
    """
    def __init__(self):
        # { symbol: { "side": str, "entry_price": float } }
        self.positions: Dict[str, Dict[str, float]] = {}

    def update_position(self, symbol: str, side: str, entry_price: float) -> None:
        """
        symbol에 대해 새로운 포지션을 기록합니다.
        :param symbol: 거래 심볼 (예: "BTCUSDT")
        :param side:   진입 방향 ("LONG" 또는 "SHORT")
        :param entry_price: 진입 가격
        """
        self.positions[symbol] = {
            "side": side,
            "entry_price": entry_price
        }

    def get_position(self, symbol: str) -> Dict[str, float] | None:
        """
        symbol에 대한 현재 포지션을 반환합니다.
        포지션이 없으면 None을 반환합니다.
        """
        return self.positions.get(symbol)
