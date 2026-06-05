def detectar_explosoes(ranking, limite=5):
    explosoes = []

    for item in ranking:
        v = item.get("velocidade", {})
        score = item.get("score", 0)

        dif_1 = v.get("diferenca", 0)
        dif_3 = v.get("diferenca_3c", 0)
        dif_6 = v.get("diferenca_6c", 0)

        status = v.get("status", "estável")

        if status == "explodindo" or dif_3 >= 25 or dif_6 >= 35:
            explosoes.append({
                "nome": item["nome"],
                "score": score,
                "nivel": item.get("nivel"),
                "dif_1": dif_1,
                "dif_3": dif_3,
                "dif_6": dif_6,
                "fontes": item.get("fontes", []),
                "influenciadores": item.get("influenciadores", []),
                "reddit_mencoes": item.get("reddit_mencoes", 0),
                "rss_mencoes": item.get("rss_mencoes", 0),
                "infl_mencoes": item.get("infl_mencoes", 0),
            })

    explosoes.sort(key=lambda x: (x["dif_6"], x["dif_3"], x["score"]), reverse=True)
    return explosoes[:limite]

def formatar_explosoes(explosoes):
    if not explosoes:
        return ""

    linhas = [
        "🚨 <b>Narrativas Explodindo</b>",
        "",
        "Narrativas com maior aceleração recente:",
        ""
    ]

    for i, item in enumerate(explosoes, start=1):
        fontes = " + ".join(item["fontes"]) if item["fontes"] else "Sem fonte"
        kols = ", ".join(item["influenciadores"][:4]) if item["influenciadores"] else "Sem KOLs detectados"

        linhas.append(
            f"{i}. 🚀 <b>{item['nome']}</b> — Score {item['score']}/100 ({item['nivel']})\n"
            f"   Crescimento 1 ciclo: {item['dif_1']:+.1f}\n"
            f"   Crescimento 3 ciclos: {item['dif_3']:+.1f}\n"
            f"   Crescimento 6 ciclos: {item['dif_6']:+.1f}\n"
            f"   Fontes: {fontes}\n"
            f"   KOLs: {kols}\n"
            f"   Sinais: {item['infl_mencoes']} KOLs | {item['reddit_mencoes']} Reddit | {item['rss_mencoes']} notícias"
        )

    return "\n".join(linhas)
