from .narrative_tokens import MAPA_NARRATIVA_TOKENS, criar_indice_tokens, money

def gerar_narrative_dex(ranking, tokens_mercado, limite_narrativas=7, limite_tokens=5):
    indice = criar_indice_tokens(tokens_mercado)
    resultado = []

    for narrativa in ranking[:limite_narrativas]:
        nome = narrativa["nome"]
        symbols = MAPA_NARRATIVA_TOKENS.get(nome, [])

        tokens = []

        for symbol in symbols:
            token = indice.get(symbol)

            if not token:
                continue

            variacao = token.get("variacao_24h") or 0
            volume = token.get("volume_24h") or 0
            market_cap = token.get("market_cap") or 0

            forca = 0
            forca += max(min(variacao, 30), -30)
            forca += min(volume / 100_000_000, 30)
            forca += min(market_cap / 1_000_000_000, 20)

            tokens.append({
                "symbol": symbol,
                "nome": token.get("nome"),
                "variacao_24h": variacao,
                "volume_24h": volume,
                "market_cap": market_cap,
                "forca": round(forca, 1),
            })

        tokens.sort(key=lambda x: x["forca"], reverse=True)

        if tokens:
            resultado.append({
                "narrativa": nome,
                "score_narrativa": narrativa["score"],
                "nivel": narrativa["nivel"],
                "tokens": tokens[:limite_tokens],
            })

    return resultado

def formatar_narrative_dex(dados):
    if not dados:
        return ""

    linhas = [
        "🧬 <b>Narrative Dex</b>",
        "",
        "Tokens que estão capturando força dentro das principais narrativas:",
        ""
    ]

    for item in dados:
        linhas.append(
            f"🔥 <b>{item['narrativa']}</b> — Score narrativo {item['score_narrativa']}/100 ({item['nivel']})"
        )

        for i, token in enumerate(item["tokens"], start=1):
            var = token["variacao_24h"]
            emoji = "🟢" if var >= 0 else "🔴"

            linhas.append(
                f"{i}. {emoji} <b>{token['symbol']}</b> — {var:+.2f}% | "
                f"Vol: {money(token['volume_24h'])} | MC: {money(token['market_cap'])}"
            )

        linhas.append("")

    linhas.append("⚠️ Radar narrativo, não recomendação de compra.")

    return "\n".join(linhas)
