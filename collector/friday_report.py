import asyncio

from .weekly_report import analisar_periodo, gerar_ideias_conteudo
from .telegram_client import send_telegram_message

def formatar_relatorio_sexta(resultados):
    if not resultados:
        return "🔥 <b>Radar de Sexta-feira</b>\n\nAinda não há histórico suficiente."

    crescimento = sorted(resultados, key=lambda x: x["crescimento"], reverse=True)[:5]
    dominantes = sorted(resultados, key=lambda x: (x["ultimo"], x["media"]), reverse=True)[:5]

    linhas = [
        "🔥 <b>Radar de Sexta-feira do Caçador de Narrativas</b>",
        "",
        "Leitura rápida para acompanhar narrativas no fim de semana.",
        "",
        "🚀 <b>Narrativas que mais cresceram nos últimos 7 dias</b>",
        ""
    ]

    for i, item in enumerate(crescimento, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   {item['primeiro']} → {item['ultimo']} ({item['crescimento']:+.1f})"
        )

    linhas += [
        "",
        "👀 <b>Narrativas para monitorar no fim de semana</b>",
        ""
    ]

    for i, item in enumerate(dominantes, start=1):
        linhas.append(
            f"{i}. <b>{item['nome']}</b>\n"
            f"   Score atual: {item['ultimo']}/100 | Média: {item['media']}/100"
        )

    linhas += [
        "",
        "💡 <b>Pautas rápidas para o X</b>",
        ""
    ]

    for i, ideia in enumerate(gerar_ideias_conteudo(dominantes), start=1):
        linhas.append(f"{i}. {ideia}")

    linhas.append("")
    linhas.append("⚠️ Use como radar de atenção, não como recomendação de compra.")

    return "\n".join(linhas)

async def main():
    resultados = analisar_periodo(dias=7)
    mensagem = formatar_relatorio_sexta(resultados)
    await send_telegram_message(mensagem)

if __name__ == "__main__":
    asyncio.run(main())
