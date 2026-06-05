import json
from pathlib import Path
from datetime import datetime, timezone

HISTORY_PATH = Path("data/narrative_history.json")

def carregar_historico():
    if not HISTORY_PATH.exists():
        return {}

    try:
        return json.loads(HISTORY_PATH.read_text())
    except Exception:
        return {}

def salvar_historico(historico):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(historico, ensure_ascii=False, indent=2))

def atualizar_historico(ranking):
    historico = carregar_historico()
    agora = datetime.now(timezone.utc).isoformat()

    for item in ranking:
        nome = item["nome"]
        historico.setdefault(nome, [])
        historico[nome].append({
            "score": item["score"],
            "nivel": item["nivel"],
            "data": agora,
        })

        historico[nome] = historico[nome][-500:]

    salvar_historico(historico)
    return historico

def _comparar(score_atual, score_anterior):
    if score_anterior is None:
        return {
            "score_anterior": None,
            "diferenca": 0,
            "crescimento_pct": 0,
        }

    diferenca = round(score_atual - score_anterior, 1)

    if score_anterior <= 0:
        crescimento_pct = 0
    else:
        crescimento_pct = round((diferenca / score_anterior) * 100, 1)

    return {
        "score_anterior": score_anterior,
        "diferenca": diferenca,
        "crescimento_pct": crescimento_pct,
    }

def calcular_velocidade(nome, score_atual, historico):
    pontos = historico.get(nome, [])

    if len(pontos) < 2:
        return {
            "score_anterior": None,
            "diferenca": 0,
            "crescimento_pct": 0,
            "diferenca_3c": 0,
            "diferenca_6c": 0,
            "status": "novo"
        }

    anterior_1 = pontos[-2]["score"]
    anterior_3 = pontos[-4]["score"] if len(pontos) >= 4 else anterior_1
    anterior_6 = pontos[-7]["score"] if len(pontos) >= 7 else anterior_3

    c1 = _comparar(score_atual, anterior_1)
    c3 = _comparar(score_atual, anterior_3)
    c6 = _comparar(score_atual, anterior_6)

    diferenca = c1["diferenca"]
    diferenca_3c = c3["diferenca"]
    diferenca_6c = c6["diferenca"]

    if diferenca >= 20 or diferenca_3c >= 30 or diferenca_6c >= 40:
        status = "explodindo"
    elif diferenca >= 10 or diferenca_3c >= 18:
        status = "acelerando forte"
    elif diferenca >= 5 or diferenca_3c >= 10:
        status = "acelerando"
    elif diferenca <= -15 or diferenca_3c <= -25:
        status = "perdendo força"
    else:
        status = "estável"

    return {
        "score_anterior": c1["score_anterior"],
        "diferenca": diferenca,
        "crescimento_pct": c1["crescimento_pct"],
        "diferenca_3c": diferenca_3c,
        "crescimento_3c_pct": c3["crescimento_pct"],
        "diferenca_6c": diferenca_6c,
        "crescimento_6c_pct": c6["crescimento_pct"],
        "status": status
    }

def aplicar_velocidade(ranking, historico):
    for item in ranking:
        vel = calcular_velocidade(item["nome"], item["score"], historico)
        item["velocidade"] = vel

    return ranking

def formatar_velocidade_narrativas(ranking, limite=5):
    acelerando = [
        item for item in ranking
        if item.get("velocidade", {}).get("status") in {
            "acelerando", "acelerando forte", "explodindo"
        }
    ]

    if not acelerando:
        return ""

    acelerando.sort(
        key=lambda x: (
            x["velocidade"].get("diferenca_3c", 0),
            x["velocidade"].get("diferenca", 0)
        ),
        reverse=True
    )

    linhas = [
        "",
        "📈 <b>Narrativas ganhando velocidade</b>",
        "",
        "Crescimento comparado aos ciclos anteriores:",
        ""
    ]

    for i, item in enumerate(acelerando[:limite], start=1):
        v = item["velocidade"]
        anterior = v["score_anterior"]
        status = v["status"]

        emoji = "🚀" if status == "explodindo" else "🔥" if status == "acelerando forte" else "🟢"

        linhas.append(
            f"{i}. {emoji} <b>{item['nome']}</b>\n"
            f"   Último ciclo: {anterior} → {item['score']} ({v['diferenca']:+.1f})\n"
            f"   Últimos 3 ciclos: {v['diferenca_3c']:+.1f}\n"
            f"   Status: {status}"
        )

    return "\n".join(linhas)
