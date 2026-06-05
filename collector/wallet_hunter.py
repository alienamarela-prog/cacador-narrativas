import httpx
from collections import defaultdict

from .config import ETHERSCAN_API_KEY, WALLET_HUNTER_ADDRESSES
from .token_narratives import TOKEN_NARRATIVAS

ETHERSCAN_V2 = "https://api.etherscan.io/v2/api"

def carregar_carteiras():
    """
    Formato esperado:
    Label|0xEndereco,Outro Label|0xEndereco
    """
    carteiras = []

    raw = WALLET_HUNTER_ADDRESSES.strip()
    if not raw:
        return carteiras

    for item in raw.split(","):
        if "|" not in item:
            continue

        label, address = item.split("|", 1)
        label = label.strip()
        address = address.strip()

        if label and address.startswith("0x"):
            carteiras.append({
                "label": label,
                "address": address,
            })

    return carteiras

def narrativa_do_token(symbol):
    symbol = (symbol or "").upper()
    n = TOKEN_NARRATIVAS.get(symbol)

    if not n:
        return "Sem narrativa mapeada"

    if isinstance(n, list):
        return ", ".join(n)

    return str(n)

async def buscar_transferencias(address, limit=25):
    if not ETHERSCAN_API_KEY:
        return []

    params = {
        "chainid": "1",
        "module": "account",
        "action": "tokentx",
        "address": address,
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
    return result if isinstance(result, list) else []

async def gerar_wallet_hunter():
    carteiras = carregar_carteiras()

    if not carteiras:
        return {
            "ativo": False,
            "motivo": "Nenhuma carteira configurada em WALLET_HUNTER_ADDRESSES.",
            "carteiras": [],
            "tokens": [],
            "narrativas": [],
        }

    tokens = defaultdict(lambda: {
        "symbol": "",
        "token_name": "",
        "qtd_transferencias": 0,
        "carteiras": set(),
        "narrativa": "",
    })

    narrativas = defaultdict(lambda: {
        "narrativa": "",
        "qtd_transferencias": 0,
        "tokens": set(),
        "carteiras": set(),
    })

    for carteira in carteiras:
        try:
            txs = await buscar_transferencias(carteira["address"])

            for tx in txs:
                symbol = (tx.get("tokenSymbol") or "").upper()
                token_name = tx.get("tokenName") or symbol

                if not symbol:
                    continue

                narrativa = narrativa_do_token(symbol)

                tokens[symbol]["symbol"] = symbol
                tokens[symbol]["token_name"] = token_name
                tokens[symbol]["qtd_transferencias"] += 1
                tokens[symbol]["carteiras"].add(carteira["label"])
                tokens[symbol]["narrativa"] = narrativa

                narrativas[narrativa]["narrativa"] = narrativa
                narrativas[narrativa]["qtd_transferencias"] += 1
                narrativas[narrativa]["tokens"].add(symbol)
                narrativas[narrativa]["carteiras"].add(carteira["label"])

        except Exception as e:
            print(f"[Wallet Hunter] erro em {carteira['label']}: {e}")

    tokens_lista = []
    for item in tokens.values():
        tokens_lista.append({
            "symbol": item["symbol"],
            "token_name": item["token_name"],
            "qtd_transferencias": item["qtd_transferencias"],
            "carteiras": sorted(item["carteiras"]),
            "narrativa": item["narrativa"],
        })

    narrativas_lista = []
    for item in narrativas.values():
        narrativas_lista.append({
            "narrativa": item["narrativa"],
            "qtd_transferencias": item["qtd_transferencias"],
            "tokens": sorted(item["tokens"]),
            "carteiras": sorted(item["carteiras"]),
        })

    tokens_lista.sort(key=lambda x: x["qtd_transferencias"], reverse=True)
    narrativas_lista.sort(key=lambda x: x["qtd_transferencias"], reverse=True)

    return {
        "ativo": True,
        "motivo": "",
        "carteiras": carteiras,
        "tokens": tokens_lista[:20],
        "narrativas": narrativas_lista[:10],
    }

def formatar_wallet_hunter(data):
    if not data:
        return ""

    if not data.get("ativo"):
        return ""

    narrativas = data.get("narrativas", [])
    tokens = data.get("tokens", [])

    if not narrativas and not tokens:
        return ""

    linhas = [
        "🐋 <b>Wallet Hunter</b>",
        "",
        "Movimentações recentes detectadas nas carteiras monitoradas:",
        ""
    ]

    if narrativas:
        linhas.append("🔥 <b>Narrativas com movimentação</b>")
        linhas.append("")

        for i, item in enumerate(narrativas[:5], start=1):
            linhas.append(
                f"{i}. <b>{item['narrativa']}</b>\n"
                f"   Transferências: {item['qtd_transferencias']}\n"
                f"   Tokens: {', '.join(item['tokens'][:6])}\n"
                f"   Carteiras: {', '.join(item['carteiras'][:4])}"
            )

    if tokens:
        linhas.append("")
        linhas.append("🪙 <b>Tokens mais movimentados</b>")
        linhas.append("")

        for i, item in enumerate(tokens[:8], start=1):
            linhas.append(
                f"{i}. <b>{item['symbol']}</b> — {item['qtd_transferencias']} transferências\n"
                f"   Narrativa: {item['narrativa']}\n"
                f"   Carteiras: {', '.join(item['carteiras'][:4])}"
            )

    linhas.append("")
    linhas.append("⚠️ Movimentação onchain não é recomendação de compra.")

    return "\n".join(linhas)
