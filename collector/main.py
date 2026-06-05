import asyncio
import time
import logging

from .config import POLL_INTERVAL_SECONDS, TOP_N_TOKENS, ALERT_THRESHOLD, ALERT_COOLDOWN_MINUTES, RUN_ONCE, OUTPUT_MODE
from .coingecko import fetch_top_tokens
from .social import fetch_social_signals
from .scoring import narrative_score
from .telegram_client import send_telegram_message
from .filters import is_allowed_token
from .trending import fetch_trending_symbols
from .dexscreener import fetch_dex_boosted_symbols
from .rss_signals import fetch_rss_narratives
from .reddit_signals import fetch_reddit_narratives
from .influencers import fetch_influencer_narratives
from .narrative_engine import gerar_ranking_narrativas, formatar_ranking_narrativas
from .history import atualizar_historico, aplicar_velocidade, formatar_velocidade_narrativas
from .explosion_detector import detectar_explosoes, formatar_explosoes
from .new_narratives import detectar_narrativas_novas, formatar_narrativas_novas
from .narrative_tokens import formatar_narrativa_tokens
from .token_narratives import TOKEN_NARRATIVAS
from .narrative_dex import gerar_narrative_dex, formatar_narrative_dex
from .alpha_hunter import detectar_pre_explosao, formatar_pre_explosao
from .alien_research import gerar_alien_research, formatar_alien_research
from .snapshot import salvar_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("cacador")

_last_alert = {}

def money(value):
    if value is None:
        return "N/A"
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value/1_000:.2f}K"
    return f"${value:.2f}"

def format_top_message(scores):
    top = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]

    lines = [
        "🛸 <b>CAÇADOR DE NARRATIVAS</b>",
        "",
        "Top sinais de mercado agora:",
        ""
    ]

    for i, item in enumerate(top, start=1):
        change = item.get("price_change_24h") or 0
        arrow = "🟢" if change >= 0 else "🔴"
        lines.append(
            f"{i}. <b>{item['symbol']}</b> — Score {item['score']:.1f}\n"
            f"{arrow} 24h: {change:.2f}% | Vol: {money(item.get('volume_24h'))} | MC: {money(item.get('market_cap'))}"
            + (" | 🔥 Trending" if item.get("meta", {}).get("trending") else "")
            + (" | ⚡ DexBoost" if item.get("meta", {}).get("dex_boosted") else "")
        )

    lines.append("")
    lines.append("📊 Sinais combinando mercado, trending e DexScreener.")
    return "\n".join(lines)


def traduzir_titulo(titulo):
    traducoes = [
        ("Hyperliquid pulls back from record highs as Arthur Hayes exits position shy of $150 price target",
         "Hyperliquid recua das máximas após Arthur Hayes sair da posição antes do alvo de US$150"),
        ("Arthur Hayes dumps HYPE, NEAR as he warns of AI IPO wave",
         "Arthur Hayes vende HYPE e NEAR enquanto alerta para uma nova onda de IPOs de IA"),
        ("Why tokenization is an ETF-style market structure revolution",
         "Por que a tokenização pode transformar a estrutura do mercado como os ETFs fizeram"),
        ("Coinbase to launch token-backed mortgage down payments this summer",
         "Coinbase deve lançar entrada de financiamento imobiliário usando tokens como garantia"),
        ("Here’s what happened in crypto today",
         "O que aconteceu no mercado cripto hoje"),
        ("Republican Lawmaker Plans to Add Prediction Markets to Congressional Stock Ban Bill",
         "Deputado republicano planeja incluir mercados de previsão em projeto sobre ações no Congresso"),
    ]

    for original, pt in traducoes:
        if original.lower() in titulo.lower():
            return pt

    # fallback: mantém o título original, mas sinaliza que veio de fonte internacional
    return titulo

def nome_narrativa_pt(nome):
    mapa = {
        "Stablecoins": "Stablecoins",
        "Prediction Markets": "Mercados de previsão",
        "Bitcoin L2": "Bitcoin Layer 2",
        "Memecoins": "Memecoins",
        "AI Agents": "Agentes de IA",
        "Gaming": "Games/Web3 Gaming",
        "Restaking": "Restaking",
        "DeFi": "DeFi",
        "RWA": "RWA / Tokenização",
        "Base": "Ecossistema Base",
        "Solana": "Ecossistema Solana",
        "Hyperliquid": "Hyperliquid",
        "ZK": "ZK / Provas de conhecimento zero",
        "DePIN": "DePIN",
        "SocialFi": "SocialFi",
    }
    return mapa.get(nome, nome)

def format_rss_narratives(rss_data):
    if not rss_data:
        return ""

    top = sorted(
        rss_data.items(),
        key=lambda x: (x[1].get("source_count", 0), x[1].get("mentions", 0)),
        reverse=True
    )[:5]

    lines = [
        "",
        "🧠 <b>Narrativas detectadas em notícias cripto</b>",
        "",
        "Leitura rápida das principais narrativas citadas por veículos internacionais:",
        ""
    ]

    for i, (name, data) in enumerate(top, start=1):
        nome_pt = nome_narrativa_pt(name)
        sources = ", ".join(data.get("sources", [])[:3])
        mentions = data.get("mentions", 0)
        source_count = data.get("source_count", 0)
        examples = data.get("examples", [])

        titulo_pt = ""
        if examples:
            titulo_pt = traduzir_titulo(examples[0].get("title", ""))[:140]

        lines.append(
            f"{i}. <b>{nome_pt}</b> — {mentions} menções em {source_count} fontes\n"
            f"   Fontes: {sources}\n"
            f"   Destaque: {titulo_pt}"
        )

    return "\n".join(lines)

def nivel_por_score(score):
    if score >= 90:
        return "🚀 Explodindo"
    if score >= 80:
        return "🔥 Forte"
    if score >= 65:
        return "🟡 Promissora"
    return "⚪ Nascente"

def format_alert(item):
    change = item.get("price_change_24h") or 0
    symbol = item["symbol"]
    narrativa = TOKEN_NARRATIVAS.get(symbol, "Narrativa ainda não mapeada")
    nivel = nivel_por_score(item["score"])

    return (
        "🚨 <b>ALERTA DO CAÇADOR DE NARRATIVAS</b>\n\n"
        f"Token: <b>{symbol}</b>\n"
        f"Nome: {item['meta'].get('name')}\n\n"
        f"🏷 <b>Narrativa:</b>\n"
        f"{narrativa}\n\n"
        f"🚦 <b>Nível:</b>\n"
        f"{nivel}\n\n"
        f"📊 <b>Métricas:</b>\n"
        f"Score: <b>{item['score']:.1f}</b>\n"
        f"Variação 24h: {change:+.2f}%\n"
        f"Volume 24h: {money(item.get('volume_24h'))}\n"
        f"Market Cap: {money(item.get('market_cap'))}\n\n"
        "🧠 <b>Leitura:</b>\n"
        "Sinal forte de mercado por volume/preço. Use como radar de atenção, não como recomendação de compra."
    )

async def cycle():
    raw_tokens = await fetch_top_tokens(TOP_N_TOKENS)
    tokens = [t for t in raw_tokens if is_allowed_token(t)]
    symbols = [t["symbol"].upper() for t in tokens]
    social = await fetch_social_signals(symbols)
    trending_symbols = await fetch_trending_symbols()
    dex_boosted_symbols = await fetch_dex_boosted_symbols()

    scores = []

    for t in tokens:
        sym = t["symbol"].upper()
        sig = social.get(sym, {"mentions": 0, "sentiment": 0.0})
        is_trending = sym in trending_symbols
        is_dex_boosted = sym in dex_boosted_symbols

        score = narrative_score(
            price_change_24h=t.get("price_change_percentage_24h"),
            volume_24h=t.get("total_volume"),
            market_cap=t.get("market_cap"),
            mentions=sig["mentions"],
            sentiment=sig["sentiment"],
        )

        if is_trending:
            score = min(100, score + 12)
        if is_dex_boosted:
            score = min(100, score + 15)

        scores.append({
            "token": t["id"],
            "symbol": sym,
            "score": score,
            "mentions": sig["mentions"],
            "sentiment": sig["sentiment"],
            "price_change_24h": t.get("price_change_percentage_24h"),
            "volume_24h": t.get("total_volume"),
            "market_cap": t.get("market_cap"),
            "category": "top-volume",
            "meta": {"rank": t.get("market_cap_rank"), "name": t.get("name"), "trending": is_trending, "dex_boosted": is_dex_boosted},
        })

    rss_data = await fetch_rss_narratives()
    reddit_data = await fetch_reddit_narratives()
    influencer_data = await fetch_influencer_narratives()
    ranking_narrativas = gerar_ranking_narrativas(reddit_data, rss_data, influencer_data)
    historico = atualizar_historico(ranking_narrativas)
    ranking_narrativas = aplicar_velocidade(ranking_narrativas, historico)
    bloco_mercado = format_top_message(scores)
    bloco_noticias = format_rss_narratives(rss_data)
    bloco_ranking = formatar_ranking_narrativas(ranking_narrativas)
    bloco_velocidade = formatar_velocidade_narrativas(ranking_narrativas)
    explosoes_data = detectar_explosoes(ranking_narrativas)
    bloco_explosoes = formatar_explosoes(explosoes_data)
    bloco_novas = formatar_narrativas_novas(detectar_narrativas_novas(ranking_narrativas))
    narrative_dex_data = gerar_narrative_dex(ranking_narrativas, raw_tokens)
    bloco_narrative_dex = formatar_narrative_dex(narrative_dex_data)
    alpha_hunter_data = detectar_pre_explosao(ranking_narrativas)
    bloco_alpha_hunter = formatar_pre_explosao(alpha_hunter_data)
    alien_research_data = gerar_alien_research(ranking_narrativas)
    bloco_alien_research = formatar_alien_research(alien_research_data)

    salvar_snapshot(
        ranking=ranking_narrativas,
        alpha_hunter=alpha_hunter_data,
        alien_research=alien_research_data,
        narrative_dex=narrative_dex_data,
        explosoes=explosoes_data,
        tokens_mercado=raw_tokens,
    )

    if OUTPUT_MODE == "alerts":
        if bloco_explosoes:
            await send_telegram_message(bloco_explosoes)

        if bloco_alpha_hunter:
            await send_telegram_message(bloco_alpha_hunter)

        if bloco_alien_research:
            await send_telegram_message(bloco_alien_research)
    else:
        await send_telegram_message(bloco_mercado)

        if bloco_noticias:
            await send_telegram_message(bloco_noticias)

        if bloco_ranking:
            await send_telegram_message(bloco_ranking)

        if bloco_velocidade:
            await send_telegram_message(bloco_velocidade)

        if bloco_explosoes:
            await send_telegram_message(bloco_explosoes)

        if bloco_novas:
            await send_telegram_message(bloco_novas)

        if bloco_narrative_dex:
            await send_telegram_message(bloco_narrative_dex)

        if bloco_alpha_hunter:
            await send_telegram_message(bloco_alpha_hunter)

        if bloco_alien_research:
            await send_telegram_message(bloco_alien_research)

    log.info("Resumo enviado ao Telegram com %d scores", len(scores))

    now = time.time()
    cooldown = ALERT_COOLDOWN_MINUTES * 60

    for item in scores:
        if item["score"] >= ALERT_THRESHOLD and (now - _last_alert.get(item["token"], 0)) > cooldown:
            await send_telegram_message(format_alert(item))
            _last_alert[item["token"]] = now
            log.info("Alerta enviado para %s", item["symbol"])

async def main():
    log.info("Caçador de Narrativas — Telegram direto iniciado (loop %ds)", POLL_INTERVAL_SECONDS)

    if OUTPUT_MODE != "alerts":
        await send_telegram_message("✅ Caçador de Narrativas iniciado.")

    if RUN_ONCE:
        try:
            await cycle()
        except Exception:
            log.exception("Ciclo falhou")
        return

    while True:
        try:
            await cycle()
        except Exception:
            log.exception("Ciclo falhou — tentando novamente no próximo intervalo")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
