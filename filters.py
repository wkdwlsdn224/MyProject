# filters.py
from config import RELIABLE_SYMBOLS

async def get_reliable_symbols(client, **kwargs):
    """
    환경변수로 정의한 신뢰 심볼 리스트를 반환합니다.
    필요하다면 여기에서 Binance API를 호출해
    실제 상장 여부를 검증할 수도 있습니다.
    """
    return RELIABLE_SYMBOLS
