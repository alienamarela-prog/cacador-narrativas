MAPA_NARRATIVA_TOKENS = {
    "RWA / Tokenização": ["ONDO", "PLUME", "CFG", "XDC", "MPL"],
    "Hyperliquid": ["HYPE", "PURR"],
    "Ecossistema Base": ["AERO", "BRETT", "DEGEN", "VIRTUAL"],
    "Agentes de IA": ["VIRTUAL", "AI16Z", "GRIFFAIN", "ARC", "ELIZA"],
    "Restaking": ["EIGEN", "ETHFI", "REZ", "PENDLE"],
    "DePIN": ["RENDER", "HNT", "AKT", "IO"],
    "ZK": ["STRK", "ZK", "MINA", "MATIC"],
    "Stablecoins": ["ENA", "MKR", "LQTY", "AAVE", "SKY"],
    "DeFi": ["AAVE", "UNI", "PENDLE", "ENA", "CRV", "MKR"],
    "Ecossistema Solana": ["SOL", "JUP", "RAY", "JTO", "PYTH"],
    "Memecoins": ["DOGE", "SHIB", "PEPE", "BONK", "WIF"],
    "Mercados de previsão": ["GNO", "UMA"],
    "Bitcoin Layer 2": ["STX", "BABY", "ORDI", "SATS"],
    "SocialFi": ["DEGEN", "FRIEND"],
    "Games/Web3 Gaming": ["IMX", "RON", "GALA", "PIXEL"],
    "Airdrops": ["ZRO", "W", "TIA", "ALT"],
    "Monad": [],
    "MegaETH": [],
    "Initia": [],
    "Eclipse": [],
    "Berachain": ["BERA"],
}

def criar_indice_tokens(tokens_mercado):
    indice = {}

    for token in tokens_mercado:
        symbol = str(token.get("symbol", "")).upper()

        if not symbol:
            continue

        indice[symbol] = {
            "symbol": symbol,
            "nome": token.get("name"),
            "preco": token.get("current_price"),
            "variacao_24h": token.get("price_change_percentage_24h"),
            "volume_24h": token.get("total_volume"),
            "market_cap": token.get("market_cap"),
            "rank": token.get("market_cap_rank"),
        }

    return indice

def money(value):
    if value is None:
        return "N/A"
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value/1_000:.2f}K"
    return f"${value:.2f}"

def formatar_narrativa_tokens(ranking, tokens_mercado, limite_narrativas=5, limite_tokens=4):
    indice = criar_indice_tokens(tokens_mercado)

    linhas = [
        "🎯 <b>Tokens ligados às narrativas</b>",
        "",
        "Mapa rápido entre narrativa forte e ativos relacionados:",
        ""
    ]

    encontrou = False

    for item in ranking[:limite_narrativas]:
        nome = item["nome"]
        relacionados = MAPA_NARRATIVA_TOKENS.get(nome, [])

        dados_tokens = []

        for symbol in relacionados:
            if symbol in indice:
                dados_tokens.append(indice[symbol])

        if not dados_tokens:
            continue

        encontrou = True
        linhas.append(f"<b>{nome}</b> — Score {item['score']}/100")

        for token in dados_tokens[:limite_tokens]:
            var = token.get("variacao_24h") or 0
            emoji = "🟢" if var >= 0 else "🔴"

            linhas.append(
                f"• {emoji} <b>{token['symbol']}</b> {var:+.2f}% | "
                f"Vol: {money(token.get('volume_24h'))} | MC: {money(token.get('market_cap'))}"
            )

        linhas.append("")

    if not encontrou:
        return ""

    return "\n".join(linhas)
