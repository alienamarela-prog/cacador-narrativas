import httpx
from .config import COINGECKO_BASE

async def fetch_top_tokens(n: int = 50):
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": n,
        "page": 1,
        "price_change_percentage": "24h",
    }
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, params=params)
        r.raise_for_status()
        return r.json()
