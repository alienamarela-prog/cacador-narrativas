import html
import httpx
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

MAX_LEN = 3200

def limpar_html_quebrado(texto: str) -> str:
    return texto.replace("<0001f7e1>", "🟡")

def dividir_mensagem(texto: str, limite: int = MAX_LEN):
    texto = limpar_html_quebrado(texto)

    partes = []
    atual = ""

    for bloco in texto.split("\n\n"):
        if len(atual) + len(bloco) + 2 <= limite:
            atual = atual + ("\n\n" if atual else "") + bloco
        else:
            if atual:
                partes.append(atual)
            atual = bloco

    if atual:
        partes.append(atual)

    finais = []
    for parte in partes:
        if len(parte) <= limite:
            finais.append(parte)
        else:
            linhas = parte.split("\n")
            chunk = ""
            for linha in linhas:
                if len(chunk) + len(linha) + 1 <= limite:
                    chunk += ("\n" if chunk else "") + linha
                else:
                    if chunk:
                        finais.append(chunk)
                    chunk = linha
            if chunk:
                finais.append(chunk)

    return finais

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    respostas = []

    partes = dividir_mensagem(text)

    async with httpx.AsyncClient(timeout=30) as client:
        for i, parte in enumerate(partes, start=1):
            prefixo = f"<b>Parte {i}/{len(partes)}</b>\n\n" if len(partes) > 1 else ""
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": prefixo + parte,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }

            response = await client.post(url, json=payload)
            response.raise_for_status()
            respostas.append(response.json())

    return respostas
