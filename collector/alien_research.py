from .narrative_tokens import MAPA_NARRATIVA_TOKENS

BASE_RESEARCH = {
    "Hyperliquid": {
        "o_que_e": "Ecossistema focado em perpétuos descentralizados, com forte atenção de traders e KOLs.",
        "risco": "Narrativa muito ligada a especulação, fluxo de traders e volatilidade alta.",
        "conteudo": "Thread: por que a Hyperliquid virou uma das narrativas favoritas dos traders cripto?"
    },
    "RWA / Tokenização": {
        "o_que_e": "Narrativa de levar ativos do mundo real para blockchain, como crédito, imóveis, títulos e fundos.",
        "risco": "Depende de regulação, adoção institucional e execução dos protocolos.",
        "conteudo": "Post educativo: RWA é só hype ou a ponte real entre mercado tradicional e cripto?"
    },
    "Agentes de IA": {
        "o_que_e": "Narrativa que une cripto com agentes autônomos de IA, automação, dados e aplicações onchain.",
        "risco": "Muitos projetos ainda são experimentais e podem depender mais de hype do que produto real.",
        "conteudo": "Thread: agentes de IA na cripto explicados para humanos iniciantes."
    },
    "Stablecoins": {
        "o_que_e": "Infraestrutura de dólares digitais usada para pagamentos, liquidez, DeFi e transferência global de valor.",
        "risco": "Risco regulatório, concentração em emissores e competição entre modelos de stablecoins.",
        "conteudo": "Post: stablecoins estão virando a infraestrutura invisível do dinheiro digital?"
    },
    "DeFi": {
        "o_que_e": "Finanças descentralizadas: lending, DEXs, yield, derivativos e infraestrutura financeira onchain.",
        "risco": "Risco de smart contracts, liquidez, hacks e ciclos de alavancagem.",
        "conteudo": "Thread: DeFi voltou ou nunca saiu? O que os dados estão mostrando."
    },
    "Ecossistema Base": {
        "o_que_e": "Ecossistema da Layer 2 da Coinbase, com forte potencial em apps, SocialFi, consumidores e stablecoins.",
        "risco": "Pode depender muito do crescimento da Coinbase e da adoção de apps reais.",
        "conteudo": "Post: por que Base pode ser uma das principais portas de entrada da cripto para usuários comuns?"
    },
    "Ecossistema Solana": {
        "o_que_e": "Ecossistema focado em alta performance, trading, memecoins, DeFi, pagamentos e apps de consumo.",
        "risco": "Competição alta, volatilidade e dependência de ciclos de atenção em memecoins.",
        "conteudo": "Post: Solana ainda domina a atenção ou está entrando em uma nova fase?"
    },
    "Restaking": {
        "o_que_e": "Narrativa de reutilizar segurança/colateral para proteger novos serviços e gerar rendimento adicional.",
        "risco": "Complexidade técnica, risco sistêmico e dependência de incentivos.",
        "conteudo": "Thread: restaking explicado sem complicar — por que tanta gente fala disso?"
    },
    "DePIN": {
        "o_que_e": "Redes físicas descentralizadas: infraestrutura, computação, internet, energia e dados usando tokens.",
        "risco": "Exige adoção no mundo real, hardware, demanda real e execução operacional.",
        "conteudo": "Post: DePIN é uma das narrativas mais reais da cripto?"
    },
    "Memecoins": {
        "o_que_e": "Tokens movidos por comunidade, cultura, atenção e especulação.",
        "risco": "Altíssimo risco, volatilidade extrema e pouca sustentação fundamental em muitos casos.",
        "conteudo": "Post: memecoins são cassino ou a nova forma de comunidades criarem valor?"
    },
}

def gerar_alien_research(ranking, limite=3):
    pesquisas = []

    for item in ranking[:limite]:
        nome = item["nome"]
        base = BASE_RESEARCH.get(nome)

        if not base:
            base = {
                "o_que_e": "Narrativa emergente detectada pelo cruzamento de mercado, comunidade, notícias e influenciadores.",
                "risco": "Ainda precisa de validação. Pode ser apenas ruído temporário de mercado.",
                "conteudo": f"Post: o que está acontecendo com a narrativa {nome}?"
            }

        tokens = MAPA_NARRATIVA_TOKENS.get(nome, [])
        influenciadores = item.get("influenciadores", [])
        fontes = item.get("fontes", [])

        pesquisas.append({
            "nome": nome,
            "score": item.get("score"),
            "nivel": item.get("nivel"),
            "o_que_e": base["o_que_e"],
            "risco": base["risco"],
            "conteudo": base["conteudo"],
            "tokens": tokens[:6],
            "fontes": fontes,
            "influenciadores": influenciadores[:4],
            "infl_mencoes": item.get("infl_mencoes", 0),
            "reddit_mencoes": item.get("reddit_mencoes", 0),
            "rss_mencoes": item.get("rss_mencoes", 0),
        })

    return pesquisas

def formatar_alien_research(pesquisas):
    if not pesquisas:
        return ""

    linhas = [
        "🧠 <b>Alien Research</b>",
        "",
        "Leitura estratégica das principais narrativas do radar:",
        ""
    ]

    for i, item in enumerate(pesquisas, start=1):
        tokens = ", ".join(item["tokens"]) if item["tokens"] else "Ainda sem token principal mapeado"
        fontes = " + ".join(item["fontes"]) if item["fontes"] else "Sem fonte dominante"
        kols = ", ".join(item["influenciadores"]) if item["influenciadores"] else "Sem KOLs detectados"

        linhas.append(
            f"{i}. <b>{item['nome']}</b> — Score {item['score']}/100 ({item['nivel']})\n\n"
            f"👽 <b>O que é:</b>\n{item['o_que_e']}\n\n"
            f"📡 <b>Por que entrou no radar:</b>\n"
            f"Fontes: {fontes}\n"
            f"Sinais: {item['infl_mencoes']} KOLs | {item['reddit_mencoes']} Reddit | {item['rss_mencoes']} notícias\n"
            f"KOLs: {kols}\n\n"
            f"🪙 <b>Tokens relacionados:</b>\n{tokens}\n\n"
            f"⚠️ <b>Risco:</b>\n{item['risco']}\n\n"
            f"💡 <b>Ideia de conteúdo:</b>\n{item['conteudo']}"
        )

        if i != len(pesquisas):
            linhas.append("\n---\n")

    linhas.append("")
    linhas.append("⚠️ Pesquisa narrativa, não recomendação de investimento.")

    return "\n".join(linhas)
