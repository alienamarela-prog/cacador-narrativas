import json
from pathlib import Path
from datetime import datetime, timezone

SEEN_PATH = Path("data/seen_narratives.json")

def carregar_vistas():
    if not SEEN_PATH.exists():
        return {}

    try:
        return json.loads(SEEN_PATH.read_text())
    except Exception:
        return {}

def salvar_vistas(vistas):
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEEN_PATH.write_text(json.dumps(vistas, ensure_ascii=False, indent=2))

def detectar_narrativas_novas(ranking, score_minimo=30):
    vistas = carregar_vistas()
    agora = datetime.now(timezone.utc).isoformat()
    novas = []

    for item in ranking:
        nome = item["nome"]

        if item.get("score", 0) < score_minimo:
            continue

        if nome not in vistas:
            novas.append(item)
            vistas[nome] = {
                "primeira_vez": agora,
                "ultimo_score": item.get("score", 0),
                "nivel": item.get("nivel", ""),
            }
        else:
            vistas[nome]["ultimo_score"] = item.get("score", 0)
            vistas[nome]["nivel"] = item.get("nivel", "")
            vistas[nome]["ultima_vez"] = agora

    salvar_vistas(vistas)
    return novas

def formatar_narrativas_novas(novas, limite=5):
    if not novas:
        return ""

    linhas = [
        "🆕 <b>Narrativas Novas no Radar</b>",
        "",
        "Essas narrativas apareceram pela primeira vez no monitoramento:",
        ""
    ]

    for i, item in enumerate(novas[:limite], start=1):
        fontes = " + ".join(item.get("fontes", [])) if item.get("fontes") else "Sem fonte"
        kols = ", ".join(item.get("influenciadores", [])[:4]) if item.get("influenciadores") else "Sem KOLs detectados"

        linhas.append(
            f"{i}. <b>{item['nome']}</b> — Score {item['score']}/100 ({item['nivel']})\n"
            f"   Fontes: {fontes}\n"
            f"   KOLs: {kols}\n"
            f"   Sinais: {item.get('infl_mencoes', 0)} KOLs | "
            f"{item.get('reddit_mencoes', 0)} Reddit | "
            f"{item.get('rss_mencoes', 0)} notícias"
        )

    return "\n".join(linhas)
