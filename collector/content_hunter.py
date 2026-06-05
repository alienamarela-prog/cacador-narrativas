def gerar_content_hunter(alien_research, limite=3):
    resultados = []

    for item in alien_research[:limite]:
        narrativa = item["nome"]

        resultados.append({
            "narrativa": narrativa,
            "thread": f"Por que a narrativa {narrativa} está aparecendo em todos os radares cripto?",
            "meme": f"POV: você ignorou {narrativa} e agora ela aparece em todo lugar.",
            "post_curto": f"A narrativa {narrativa} está ganhando atenção de KOLs, Reddit e mercado ao mesmo tempo.",
        })

    return resultados


def formatar_content_hunter(conteudos):
    if not conteudos:
        return ""

    linhas = [
        "🧠 <b>Content Hunter</b>",
        "",
        "Ideias de conteúdo geradas automaticamente pelo radar:",
        ""
    ]

    for item in conteudos:
        linhas.append(
            f"🚀 <b>{item['narrativa']}</b>\n\n"
            f"🧵 Thread:\n{item['thread']}\n\n"
            f"😂 Meme:\n{item['meme']}\n\n"
            f"⚡ Post curto:\n{item['post_curto']}\n"
        )

    return "\n".join(linhas)
