import feedparser
import httpx
from datetime import datetime, timezone

# Perfis importantes do Crypto Twitter / Web3
INFLUENCIADORES = {
    "Arthur Hayes": "CryptoHayes",
    "Cobie": "cobie",
    "Hsaka": "HsakaTrades",
    "Ignas": "DefiIgnas",
    "Pentoshi": "Pentosh1",
    "Ansem": "blknoiz06",
    "The DeFi Edge": "thedefiedge",
    "Defi Dad": "DeFi_Dad",
    "Kaito": "KaitoAI",
    "Delphi Digital": "Delphi_Digital",
    "Messari": "MessariCrypto",
    "Bankless": "BanklessHQ",
    "0xMert": "0xMert_",

    # Protocolos oficiais
    "Hyperliquid": "HyperliquidX",
    "Jupiter": "JupiterExchange",
    "Monad": "monad_xyz",
    "MegaETH": "megaeth_labs",
    "Initia": "initiaFDN",
    "Berachain": "berachain",
    "Ethena": "ethena_labs",
    "Pendle": "pendle_fi",
    "Aave": "aave",
    "EigenLayer": "eigenlayer",
    "Virtuals": "virtuals_io",
    "Base": "base",
    "Farcaster": "farcaster_xyz",
}

# Instâncias públicas podem quebrar. Se uma falhar, tentamos a próxima.
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
]

NARRATIVAS = {
    "Agentes de IA": ["ai agent", "ai agents", "agent", "agents", "virtuals", "ai16z", "eliza", "autonomous"],
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
    "Ecossistema Base": ["base", "base chain", "base ecosystem", "coinbase l2"],
    "Ecossistema Solana": ["solana", "jupiter", "pump.fun", "raydium"],
    "Hyperliquid": ["hyperliquid", "hype"],
    "Airdrops": ["airdrop", "airdrop farming", "points", "testnet", "quest"],
    "Monad": ["monad"],
    "MegaETH": ["megaeth"],
    "Initia": ["initia"],
    "Eclipse": ["eclipse"],
    "Berachain": ["berachain", "bera"],
}

async def fetch_url(url: str):
    headers = {
        "User-Agent": "CacadorDeNarrativas/1.0"
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

async def fetch_profile_feed(username: str):
    erros = []

    for base in NITTER_INSTANCES:
        url = f"{base}/{username}/rss"

        try:
            raw = await fetch_url(url)
            feed = feedparser.parse(raw)

            if feed.entries:
                return feed.entries[:8]

        except Exception as e:
            erros.append(f"{base}: {e}")

    print(f"[Influenciadores] falhou @{username}: " + " | ".join(erros[:2]))
    return []

async def fetch_influencer_narratives():
    resultados = {}

    for nome, username in INFLUENCIADORES.items():
        entries = await fetch_profile_feed(username)

        for entry in entries:
            titulo = getattr(entry, "title", "") or ""
            resumo = getattr(entry, "summary", "") or ""
            link = getattr(entry, "link", "") or ""

            texto = f"{titulo} {resumo}".lower()

            for narrativa, palavras in NARRATIVAS.items():
                hits = [p for p in palavras if p.lower() in texto]

                if hits:
                    item = resultados.setdefault(narrativa, {
                        "mencoes": 0,
                        "influenciadores": set(),
                        "exemplos": [],
                        "palavras": set(),
                    })

                    item["mencoes"] += 1
                    item["influenciadores"].add(nome)
                    item["palavras"].update(hits)

                    if len(item["exemplos"]) < 3:
                        item["exemplos"].append({
                            "influenciador": nome,
                            "titulo": titulo[:180],
                            "url": link,
                        })

    limpo = {}

    for narrativa, data in resultados.items():
        limpo[narrativa] = {
            "mencoes": data["mencoes"],
            "quantidade_influenciadores": len(data["influenciadores"]),
            "influenciadores": sorted(data["influenciadores"]),
            "palavras": sorted(data["palavras"]),
            "exemplos": data["exemplos"],
            "detectado_em": datetime.now(timezone.utc).isoformat(),
        }

    return limpo
