import httpx
from collections import defaultdict
from .config import ETHERSCAN_API_KEY

ETHERSCAN_V2 = "https://api.etherscan.io/v2/api"

TOKENS_SEMENTE = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
}

IGNORAR = {
    "0x0000000000000000000000000000000000000000",
}

async def buscar_txs_token(symbol, contract, limit=50):
    params = {
        "chainid": "1",
        "module": "account",
        "action": "tokentx",
        "contractaddress": contract,
        "page": "1",
        "offset": str(limit),
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(ETHERSCAN_V2, params=params)
        r.raise_for_status()
        data = r.json()

    result = data.get("result", [])
    if not isinstance(result, list):
        return []

    return result

async def descobrir_carteiras():
    score = defaultdict(lambda: {
        "address": "",
        "tokens": set(),
        "qtd_transferencias": 0,
        "entradas": 0,
        "saidas": 0,
    })

    for symbol, contract in TOKENS_SEMENTE.items():
        try:
            txs = await buscar_txs_token(symbol, contract)

            for tx in txs:
                from_addr = (tx.get("from") or "").lower()
                to_addr = (tx.get("to") or "").lower()

                for addr, tipo in [(from_addr, "saida"), (to_addr, "entrada")]:
                    if not addr or addr in IGNORAR:
                        continue

                    score[addr]["address"] = addr
                    score[addr]["tokens"].add(symbol)
                    score[addr]["qtd_transferencias"] += 1

                    if tipo == "entrada":
                        score[addr]["entradas"] += 1
                    else:
                        score[addr]["saidas"] += 1

        except Exception as e:
            print(f"[Wallet Discovery] erro em {symbol}: {e}")

    carteiras = []

    for item in score.values():
        tokens = sorted(item["tokens"])
        pontos = item["qtd_transferencias"] + (len(tokens) * 3)

        if item["qtd_transferencias"] < 2:
            continue

        carteiras.append({
            "address": item["address"],
            "tokens": tokens,
            "qtd_transferencias": item["qtd_transferencias"],
            "entradas": item["entradas"],
            "saidas": item["saidas"],
            "score": pontos,
        })

    carteiras.sort(key=lambda x: x["score"], reverse=True)

    return carteiras[:15]

def formatar_wallet_discovery(carteiras):
    if not carteiras:
        return ""

    linhas = [
        "🕵️ <b>Wallet Discovery</b>",
        "",
        "Carteiras candidatas encontradas automaticamente por movimentação em tokens narrativos:",
        ""
    ]

    for i, item in enumerate(carteiras[:8], start=1):
        linhas.append(
            f"{i}. <code>{item['address']}</code>\n"
            f"   Score: {item['score']}\n"
            f"   Tokens: {', '.join(item['tokens'])}\n"
            f"   Transferências: {item['qtd_transferencias']} | Entradas: {item['entradas']} | Saídas: {item['saidas']}"
        )

    linhas.append("")
    linhas.append("⚠️ Carteira candidata não significa compra, smart money confirmado ou recomendação.")

    return "\n".join(linhas)
