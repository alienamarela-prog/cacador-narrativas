import httpx

DEX_BASE = "https://api.dexscreener.com"

async def fetch_dex_boosted_symbols(limit: int = 30):
    url = f"{DEX_BASE}/token-boosts/top/v1"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    symbols = set()
    items = data[:limit] if isinstance(data, list) else []

    for item in items:
        desc = str(item.get("description", "")).upper()
        url = str(item.get("url", "")).upper()

        # fallback simples: tenta capturar símbolos mencionados no texto/url
        for part in (desc + " " + url).replace("/", " ").replace("-", " ").split():
            clean = "".join(ch for ch in part if ch.isalnum())
            if 2 <= len(clean) <= 10 and clean.isupper():
                symbols.add(clean)

    return symbols
