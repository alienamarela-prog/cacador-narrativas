PESOS_NOTICIAS = {
    "CoinDesk": 3.0,
    "The Defiant": 2.5,
    "Decrypt": 2.0,
    "CoinTelegraph": 2.0,
}

PESOS_REDDIT = {
    "r/CryptoCurrency": 1.5,
    "r/ethfinance": 1.4,
    "r/ethereum": 1.3,
    "r/defi": 1.3,
    "r/solana": 1.2,
    "r/Bitcoin": 1.0,
}

PESOS_INFLUENCIADORES = {
    "Arthur Hayes": 4.0,
    "Cobie": 4.0,
    "Ansem": 3.5,
    "Hsaka": 3.5,
    "Ignas": 3.0,
    "Pentoshi": 3.0,
    "Kaito": 3.0,
    "The DeFi Edge": 2.5,
    "Defi Dad": 2.2,
    "Delphi Digital": 2.5,
    "Messari": 2.5,
    "Bankless": 2.2,
    "0xMert": 2.5,
}

def _norm(value, max_value):
    if max_value <= 0:
        return 0
    return min(1, value / max_value)

def peso_fontes_noticias(fontes):
    return sum(PESOS_NOTICIAS.get(f, 1.0) for f in fontes)

def peso_fontes_reddit(fontes):
    return sum(PESOS_REDDIT.get(f, 1.0) for f in fontes)

def peso_influenciadores(nomes):
    return sum(PESOS_INFLUENCIADORES.get(n, 1.5) for n in nomes)

def calcular_score_narrativa(nome, dados_reddit=None, dados_rss=None, dados_influenciadores=None):
    dados_reddit = dados_reddit or {}
    dados_rss = dados_rss or {}
    dados_influenciadores = dados_influenciadores or {}

    reddit_mencoes = dados_reddit.get("mencoes", 0)
    reddit_fontes = dados_reddit.get("fontes", [])
    reddit_peso = peso_fontes_reddit(reddit_fontes)

    rss_mencoes = dados_rss.get("mentions", 0)
    rss_fontes = dados_rss.get("sources", [])
    rss_peso = peso_fontes_noticias(rss_fontes)

    infl_mencoes = dados_influenciadores.get("mencoes", 0)
    infl_nomes = dados_influenciadores.get("influenciadores", [])
    infl_peso = peso_influenciadores(infl_nomes)

    score_reddit = _norm(reddit_mencoes, 20) * 18 + _norm(reddit_peso, 6) * 12
    score_noticias = _norm(rss_mencoes, 10) * 18 + _norm(rss_peso, 7) * 12
    score_influenciadores = _norm(infl_mencoes, 10) * 22 + _norm(infl_peso, 12) * 28

    score = score_reddit + score_noticias + score_influenciadores

    fontes_ativas = sum([
        1 if reddit_mencoes > 0 else 0,
        1 if rss_mencoes > 0 else 0,
        1 if infl_mencoes > 0 else 0,
    ])

    if fontes_ativas >= 2:
        score += 8

    if fontes_ativas >= 3:
        score += 7

    return round(min(100, score), 1)

def classificar_nivel(score):
    if score >= 85:
        return "Explosiva"
    if score >= 70:
        return "Forte"
    if score >= 50:
        return "Promissora"
    if score >= 30:
        return "Nascente"
    return "Fraca"

def gerar_ranking_narrativas(reddit_data, rss_data, influencer_data=None):
    influencer_data = influencer_data or {}
    nomes = set(reddit_data.keys()) | set(rss_data.keys()) | set(influencer_data.keys())
    ranking = []

    for nome in nomes:
        dados_reddit = reddit_data.get(nome, {})
        dados_rss = rss_data.get(nome, {})
        dados_infl = influencer_data.get(nome, {})

        score = calcular_score_narrativa(nome, dados_reddit, dados_rss, dados_infl)

        fontes = []
        if dados_reddit:
            fontes.append("Reddit")
        if dados_rss:
            fontes.append("Notícias")
        if dados_infl:
            fontes.append("Influenciadores")

        exemplos = []
        exemplos.extend(dados_infl.get("exemplos", [])[:1])
        exemplos.extend(dados_reddit.get("exemplos", [])[:1])
        exemplos.extend(dados_rss.get("examples", [])[:1])

        ranking.append({
            "nome": nome,
            "score": score,
            "nivel": classificar_nivel(score),
            "fontes": fontes,
            "reddit_mencoes": dados_reddit.get("mencoes", 0),
            "reddit_fontes": dados_reddit.get("quantidade_fontes", 0),
            "reddit_peso_fontes": round(peso_fontes_reddit(dados_reddit.get("fontes", [])), 1),
            "rss_mencoes": dados_rss.get("mentions", 0),
            "rss_fontes": dados_rss.get("source_count", 0),
            "rss_peso_fontes": round(peso_fontes_noticias(dados_rss.get("sources", [])), 1),
            "infl_mencoes": dados_infl.get("mencoes", 0),
            "infl_count": dados_infl.get("quantidade_influenciadores", 0),
            "infl_peso": round(peso_influenciadores(dados_infl.get("influenciadores", [])), 1),
            "influenciadores": dados_infl.get("influenciadores", []),
            "exemplos": exemplos,
        })

    ranking.sort(key=lambda x: x["score"], reverse=True)
    return ranking

def formatar_ranking_narrativas(ranking, limite=7):
    if not ranking:
        return ""

    linhas = [
        "",
        "🔥 <b>Ranking de Narrativas Emergentes</b>",
        "",
        "Pontuação ponderada por notícias, Reddit e influenciadores:",
        ""
    ]

    for i, item in enumerate(ranking[:limite], start=1):
        fontes = " + ".join(item["fontes"]) if item["fontes"] else "Sem fonte"
        emoji = "🚀" if item["score"] >= 85 else "🔥" if item["score"] >= 70 else "🟡" if item["score"] >= 50 else "⚪"

        infl_linha = ""
        if item.get("influenciadores"):
            nomes = ", ".join(item["influenciadores"][:4])
            infl_linha = f"\n   KOLs: {nomes}"

        linhas.append(
            f"{i}. {emoji} <b>{item['nome']}</b> — Score {item['score']}/100 ({item['nivel']})\n"
            f"   Fontes: {fontes}\n"
            f"   Influenciadores: {item['infl_mencoes']} menções | peso {item['infl_peso']}{infl_linha}\n"
            f"   Reddit: {item['reddit_mencoes']} menções | peso {item['reddit_peso_fontes']}\n"
            f"   Notícias: {item['rss_mencoes']} menções | peso {item['rss_peso_fontes']}"
        )

    return "\n".join(linhas)
