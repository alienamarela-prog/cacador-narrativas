def detectar_pre_explosao(ranking, limite=5):
    sinais = []

    for item in ranking:
        score = item.get("score", 0)
        infl = item.get("infl_mencoes", 0)
        reddit = item.get("reddit_mencoes", 0)
        noticias = item.get("rss_mencoes", 0)
        fontes = item.get("fontes", [])

        # Narrativa ainda antes da mídia, mas com sinal social/comunidade
        social_forte = infl >= 3 or reddit >= 8
        pouca_midia = noticias <= 1
        score_interessante = 30 <= score <= 85

        if social_forte and pouca_midia and score_interessante:
            sinais.append({
                "nome": item["nome"],
                "score": score,
                "nivel": item.get("nivel"),
                "fontes": fontes,
                "influenciadores": item.get("influenciadores", []),
                "infl_mencoes": infl,
                "reddit_mencoes": reddit,
                "rss_mencoes": noticias,
            })

    sinais.sort(
        key=lambda x: (x["infl_mencoes"], x["reddit_mencoes"], x["score"]),
        reverse=True
    )

    return sinais[:limite]

def formatar_pre_explosao(sinais):
    if not sinais:
        return ""

    linhas = [
        "⚡ <b>Alpha Hunter — Pré-explosão detectada</b>",
        "",
        "Narrativas com força social/comunidade antes de virarem manchete:",
        ""
    ]

    for i, item in enumerate(sinais, start=1):
        kols = ", ".join(item["influenciadores"][:4]) if item["influenciadores"] else "Sem KOLs detectados"

        linhas.append(
            f"{i}. <b>{item['nome']}</b> — Score {item['score']}/100 ({item['nivel']})\n"
            f"   KOLs: {item['infl_mencoes']} menções\n"
            f"   Reddit: {item['reddit_mencoes']} menções\n"
            f"   Notícias: {item['rss_mencoes']} menções\n"
            f"   Influenciadores: {kols}\n"
            f"   Leitura: possível narrativa antes da mídia."
        )

    linhas.append("")
    linhas.append("⚠️ Radar de atenção, não recomendação de compra.")

    return "\n".join(linhas)
