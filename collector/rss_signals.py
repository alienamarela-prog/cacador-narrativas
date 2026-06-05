import feedparser
import httpx
from datetime import datetime, timezone

RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "The Defiant": "https://thedefiant.io/feed/",
    "Decrypt": "https://decrypt.co/feed",
}

NARRATIVES = {
    "AI Agents": ["ai agent", "agents", "autonomous agent", "virtuals", "ai16z", "eliza"],
    "RWA": ["rwa", "real world asset", "tokenized", "tokenization", "blackrock", "ondo"],
    "DePIN": ["depin", "render", "helium", "akash", "decentralized physical"],
    "Restaking": ["restaking", "eigenlayer", "eigen", "avs", "karak", "symbiotic"],
    "ZK": ["zero knowledge", "zk", "zkproof", "starknet", "zksync"],
    "Stablecoins": ["stablecoin", "usdc", "usdt", "tether", "circle", "yield-bearing stablecoin"],
    "SocialFi": ["socialfi", "farcaster", "lens", "degen"],
    "Gaming": ["gaming", "gamefi", "web3 game", "ronin", "immutable"],
    "Bitcoin L2": ["bitcoin layer 2", "bitcoin l2", "stacks", "babylon", "ordinals", "runes"],
    "Memecoins": ["memecoin", "meme coin", "pepe", "doge", "shib", "bonk", "wif"],
    "Prediction Markets": ["prediction market", "polymarket", "kalshi"],
    "DeFi": ["defi", "aave", "uniswap", "lending", "dex", "yield"],
    "Base": ["base", "coinbase layer 2", "base chain"],
    "Solana": ["solana", "jupiter", "pump.fun", "raydium"],
    "Hyperliquid": ["hyperliquid", "hype"],
}

async def fetch_feed(url: str):
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

async def fetch_rss_narratives():
    results = {}

    for source, url in RSS_FEEDS.items():
        try:
            raw = await fetch_feed(url)
            feed = feedparser.parse(raw)

            for entry in feed.entries[:12]:
                title = getattr(entry, "title", "") or ""
                summary = getattr(entry, "summary", "") or ""
                link = getattr(entry, "link", "") or ""
                text = f"{title} {summary}".lower()

                for narrative, keywords in NARRATIVES.items():
                    hits = [kw for kw in keywords if kw.lower() in text]
                    if hits:
                        item = results.setdefault(narrative, {
                            "mentions": 0,
                            "sources": set(),
                            "examples": [],
                            "keywords": set(),
                        })
                        item["mentions"] += 1
                        item["sources"].add(source)
                        item["keywords"].update(hits)

                        if len(item["examples"]) < 3:
                            item["examples"].append({
                                "source": source,
                                "title": title[:160],
                                "url": link,
                            })

        except Exception as e:
            print(f"[RSS] erro em {source}: {e}")

    clean = {}
    for narrative, data in results.items():
        clean[narrative] = {
            "mentions": data["mentions"],
            "source_count": len(data["sources"]),
            "sources": sorted(data["sources"]),
            "keywords": sorted(data["keywords"]),
            "examples": data["examples"],
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }

    return clean
