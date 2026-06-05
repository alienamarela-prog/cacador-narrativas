import httpx
from .config import COINGECKO_BASE

async def fetch_trending_symbols():
    url = f"{COINGECKO_BASE}/search/trending"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    symbols = set()

    for item in data.get("coins", []):
        coin = item.get("item", {})
        symbol = str(coin.get("symbol", "")).upper()
        if symbol:
            symbols.add(symbol)

    return symbols
