import asyncio
from datetime import datetime, timezone, timedelta

from .history import carregar_historico
from .telegram_client import send_telegram_message

def media(valores):
    return round(sum(valores) / len(valores), 1) if valores else 0

def pontos_ultimos_dias(pontos, dias=7):
    limite = datetime.now(timezone.utc) - timedelta(days=dias)
    filtrados = []

    for p in pontos:
        try:
            data = datetime.fromisoformat(p.get("data"))
            if data >= limite:
                filtrados.append(p)
        except Exception:
            continue

    return filtrados

def analisar_periodo(dias=7):
    historico = carregar_historico()
    resultados = []

    for nome, pontos in historico.items():
        pontos = pontos_ultimos_dias(pontos, dias=dias)

        if not pontos:
            continue

        scores = [p.get("score", 0) for p in pontos]
        primeiro = scores[0]
        ultimo = scores[-1]
        maximo = max(scores)
        media_score = media(scores)
        ciclos_top = sum(1 for s in scores if s >= 70)
        crescimento = round(ultimo - primeiro, 1)

        crescimento_pct = round((crescimento / primeiro) * 100, 1) if primeiro > 0 else 0

        resultados.append({
            "nome": nome,
            "primeiro": primeiro,
            "ultimo": ultimo,
            "maximo": maximo,
            "media": media_score,
            "ciclos_top": ciclos_top,
            "crescimento": crescimento,
            "crescimento_pct": crescimento_pct,
            "leituras": len(scores),
        })

    return resultados

def gerar_ideias_conteudo(top_narrativas):
    ideias = []

    for item in top_narrativas[:5]:
        nome = item["nome"]

        if "Hyperliquid" in nome:
            ideias.append("Thread: por que Hyperliquid virou uma das narrativas mais fortes da semana?")
        elif "RWA" in nome:
            ideias.append("Post educativo: RWA e tokenização — por que o mercado está prestando atenção?")
        elif "Agentes de IA" in nome:
            ideias.append("Thread: agentes de IA na cripto explicados para humanos iniciantes.")
        elif "Stablecoins" in nome:
            ideias.append("Post: stablecoins estão virando infraestrutura financeira global?")
        elif "DeFi" in nome:
            ideias.append("Thread: DeFi voltou ou nunca saiu? O que os dados da semana mostram.")
        elif "Base" in nome:
            ideias.append("Post: por que o ecossistema Base continua aparecendo nas narrativas?")
        elif "Solana" in nome:
            ideias.append("Post comparativo: Solana ainda domina atenção ou está perdendo força?")
        else:
            ideias.append(f"Post: o que está acontecendo com a narrativa {nome}?")

    return ideias

def formatar_relatorio_semanal(resultados):
    if not resultados:
        return "📅 <b>Resumo Semanal</b>\n\nAinda não há histórico suficiente dos últimos 7 dias."

    dominantes = sorted(resultados, key=lambda x: (x["ciclos_top"], x["media"]), reverse=True)[:5]
    crescimento = sorted(resultados, key=lambda x: x["crescimento"], reverse=True)[:5]
    queda = sorted(resultados, key=lambda x: x["crescimento"])[:5]

    linhas = [
        "📅 <b>Resumo Semanal do Caçador de Narrativas</b>",
        "",
        "Período analisado: últimos 7 dias.",
        "",
        "🏆 <b>Narrativas mais consistentes da semana</b>",
        ""
    ]

    for i, item in enumerate(dominantes, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   Média: {item['media']}/100 | Máxima: {item['maximo']}/100 | Ciclos fortes: {item['ciclos_top']}"
        )

    linhas += ["", "🚀 <b>Maiores acelerações</b>", ""]

    for i, item in enumerate(crescimento, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   {item['primeiro']} → {item['ultimo']} ({item['crescimento']:+.1f})"
        )

    linhas += ["", "📉 <b>Narrativas perdendo força</b>", ""]

    for i, item in enumerate(queda, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   {item['primeiro']} → {item['ultimo']} ({item['crescimento']:+.1f})"
        )

    ideias = gerar_ideias_conteudo(dominantes)

    linhas += ["", "💡 <b>Ideias de conteúdo para a Alien Amarela</b>", ""]

    for i, ideia in enumerate(ideias, start=1):
        linhas.append(f"{i}. {ideia}")

    linhas.append("")
    linhas.append("⚠️ Radar de narrativas, não recomendação de investimento.")

    return "\n".join(linhas)

async def main():
    resultados = analisar_periodo(dias=7)
    mensagem = formatar_relatorio_semanal(resultados)
    await send_telegram_message(mensagem)

if __name__ == "__main__":
    asyncio.run(main())
