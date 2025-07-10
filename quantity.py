from config import SYMBOL_LEVERAGE

async def get_usdt_balance(client):
    bals = await client.futures_account_balance()
    for i in bals:
        if i["asset"]=="USDT":
            return float(i["balance"])
    return 0.0

async def calculate_quantity(client, symbol, usdt_balance):
    lev   = SYMBOL_LEVERAGE.get(symbol,10)
    price = float((await client.futures_mark_price(symbol=symbol))["markPrice"])
    info  = await client.get_symbol_info(symbol)
    prec  = int(info["quantityPrecision"])
    amt   = usdt_balance*0.9*lev
    qty   = max(amt/price, 1/price)
    return round(qty, prec)
