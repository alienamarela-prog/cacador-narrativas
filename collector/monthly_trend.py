import asyncio
from datetime import datetime, timezone, timedelta

from .history import carregar_historico
from .telegram_client import send_telegram_message

def media(valores):
    return round(sum(valores) / len(valores), 1) if valores else 0

def filtrar_pontos(pontos, dias=30):
    limite = datetime.now(timezone.utc) - timedelta(days=dias)
    out = []

    for p in pontos:
        try:
            data = datetime.fromisoformat(p.get("data"))
            if data >= limite:
                out.append(p)
        except Exception:
            continue

    return out

def analisar_30d():
    historico = carregar_historico()
    resultados = []

    for nome, pontos in historico.items():
        pontos = filtrar_pontos(pontos, dias=30)

        if len(pontos) < 3:
            continue

        scores = [p.get("score", 0) for p in pontos]
        inicio = scores[0]
        fim = scores[-1]
        media_score = media(scores)
        maximo = max(scores)
        minimo = min(scores)
        crescimento = round(fim - inicio, 1)
        estabilidade = round(maximo - minimo, 1)
        ciclos_fortes = sum(1 for s in scores if s >= 70)

        resultados.append({
            "nome": nome,
            "inicio": inicio,
            "fim": fim,
            "media": media_score,
            "maximo": maximo,
            "minimo": minimo,
            "crescimento": crescimento,
            "estabilidade": estabilidade,
            "ciclos_fortes": ciclos_fortes,
            "leituras": len(scores),
        })

    return resultados

def formatar_tendencia_30d(resultados):
    if not resultados:
        return "📆 <b>Tendência de 30 dias</b>\n\nAinda não há histórico suficiente."

    estruturais = sorted(
        resultados,
        key=lambda x: (x["ciclos_fortes"], x["media"]),
        reverse=True
    )[:5]

    acumulando = sorted(
        resultados,
        key=lambda x: x["crescimento"],
        reverse=True
    )[:5]

    linhas = [
        "📆 <b>Tendência Estrutural de 30 dias</b>",
        "",
        "Leitura de narrativas que não são apenas hype momentâneo.",
        "",
        "🏛 <b>Narrativas mais estruturais</b>",
        ""
    ]

    for i, item in enumerate(estruturais, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   Média: {item['media']}/100 | Máxima: {item['maximo']}/100 | Ciclos fortes: {item['ciclos_fortes']}"
        )

    linhas += [
        "",
        "📈 <b>Narrativas acumulando força</b>",
        ""
    ]

    for i, item in enumerate(acumulando, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   {item['inicio']} → {item['fim']} ({item['crescimento']:+.1f})"
        )

    linhas.append("")
    linhas.append("⚠️ Quanto mais histórico acumulado, melhor este relatório fica.")

    return "\n".join(linhas)

async def main():
    resultados = analisar_30d()
    msg = formatar_tendencia_30d(resultados)
    await send_telegram_message(msg)

if __name__ == "__main__":
    asyncio.run(main())
