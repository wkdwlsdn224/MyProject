from config import RELIABLE_SYMBOLS

async def get_reliable_symbols(client):
    info = await client.futures_exchange_info()
    return [
        s["symbol"] for s in info["symbols"]
        if s["symbol"] in RELIABLE_SYMBOLS
    ]
