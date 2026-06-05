import feedparser
import httpx
from datetime import datetime, timezone

REDDIT_FEEDS = {
    "r/CryptoCurrency": "https://www.reddit.com/r/CryptoCurrency/new/.rss",
    "r/ethereum": "https://www.reddit.com/r/ethereum/new/.rss",
    "r/ethfinance": "https://www.reddit.com/r/ethfinance/new/.rss",
    "r/solana": "https://www.reddit.com/r/solana/new/.rss",
    "r/Bitcoin": "https://www.reddit.com/r/Bitcoin/new/.rss",
    "r/defi": "https://www.reddit.com/r/defi/new/.rss",
}

NARRATIVAS = {
    "Agentes de IA": ["ai agent", "ai agents", "agent", "agents", "virtuals", "ai16z", "eliza"],
    "RWA / Tokenização": ["rwa", "real world asset", "tokenization", "tokenized", "ondo", "plume"],
    "DePIN": ["depin", "render", "helium", "akash"],
    "Restaking": ["restaking", "eigenlayer", "eigen", "avs", "karak", "symbiotic"],
    "ZK": ["zero knowledge", "zk", "starknet", "zksync"],
    "Stablecoins": ["stablecoin", "stablecoins", "usdc", "usdt", "tether", "circle"],
    "SocialFi": ["socialfi", "farcaster", "lens", "degen"],
    "Games/Web3 Gaming": ["gaming", "gamefi", "web3 game", "ronin", "immutable"],
    "Bitcoin Layer 2": ["bitcoin layer 2", "bitcoin l2", "stacks", "babylon", "ordinals", "runes"],
    "Memecoins": ["memecoin", "memecoins", "meme coin", "pepe", "doge", "shib", "bonk", "wif"],
    "Mercados de previsão": ["prediction market", "prediction markets", "polymarket", "kalshi"],
    "DeFi": ["defi", "aave", "uniswap", "lending", "dex", "yield"],
    "Ecossistema Base": ["base chain", "base ecosystem", "coinbase l2"],
    "Ecossistema Solana": ["solana", "jupiter", "pump.fun", "raydium"],
    "Hyperliquid": ["hyperliquid", "hype"],
    "Airdrops": ["airdrop", "airdrop farming", "points", "testnet", "quest"],
    "Monad": ["monad"],
    "MegaETH": ["megaeth"],
    "Initia": ["initia"],
    "Eclipse": ["eclipse"],
    "Berachain": ["berachain", "bera"],
}

async def fetch_feed(url: str):
    headers = {
        "User-Agent": "CacadorDeNarrativas/1.0"
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

async def fetch_reddit_narratives():
    resultados = {}

    for fonte, url in REDDIT_FEEDS.items():
        try:
            raw = await fetch_feed(url)
            feed = feedparser.parse(raw)

            for entry in feed.entries[:15]:
                titulo = getattr(entry, "title", "") or ""
                resumo = getattr(entry, "summary", "") or ""
                link = getattr(entry, "link", "") or ""

                texto = f"{titulo} {resumo}".lower()

                for narrativa, palavras in NARRATIVAS.items():
                    hits = [p for p in palavras if p.lower() in texto]

                    if hits:
                        item = resultados.setdefault(narrativa, {
                            "mencoes": 0,
                            "fontes": set(),
                            "exemplos": [],
                            "palavras": set(),
                        })

                        item["mencoes"] += 1
                        item["fontes"].add(fonte)
                        item["palavras"].update(hits)

                        if len(item["exemplos"]) < 3:
                            item["exemplos"].append({
                                "fonte": fonte,
                                "titulo": titulo[:160],
                                "url": link,
                            })

        except Exception as e:
            print(f"[Reddit] erro em {fonte}: {e}")

    limpo = {}

    for narrativa, data in resultados.items():
        limpo[narrativa] = {
            "mencoes": data["mencoes"],
            "quantidade_fontes": len(data["fontes"]),
            "fontes": sorted(data["fontes"]),
            "palavras": sorted(data["palavras"]),
            "exemplos": data["exemplos"],
            "detectado_em": datetime.now(timezone.utc).isoformat(),
        }

    return limpo
