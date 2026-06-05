# Caçador de Narrativas v2 — Coletor Python (Opção C)

Arquitetura híbrida: este coletor Python roda 24/7 (local, VPS, Railway, Render, Fly.io)
coletando dados de CoinGecko + sinais sociais, calcula o **Narrative Score**, e envia para
o backend Lovable, que se encarrega do Telegram (comandos /top, /daily, /status, /alerts)
e do dashboard web.

## Configuração

1. Copie `.env.example` para `.env` e preencha:
   - `LOVABLE_BASE_URL` — URL do seu projeto (já preenchida)
   - `INGEST_API_KEY` — o mesmo valor que você cadastrou em Lovable → Secrets

2. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Rode o coletor:
   ```bash
   ./scripts/run.sh
   # ou
   python -m collector.main
   ```

## O que o coletor faz

- Loop a cada `POLL_INTERVAL_SECONDS` (default 300s = 5min)
- Busca top tokens por volume na CoinGecko
- Calcula Narrative Score combinando: variação 24h, volume relativo,
  sentimento (placeholder — plug a sua fonte X/Twitter/Reddit em `collector/social.py`)
- Envia batch para `POST /api/public/ingest/scores`
- Dispara alertas em `POST /api/public/alerts/trigger` quando score > `ALERT_THRESHOLD`

O Telegram é gerenciado 100% pelo Lovable — não precisa de token no Python.

## Endpoints Lovable usados

| Endpoint | Auth | Função |
|---|---|---|
| `POST /api/public/ingest/scores` | `Authorization: Bearer $INGEST_API_KEY` | Recebe scores em batch |
| `POST /api/public/alerts/trigger` | `Authorization: Bearer $INGEST_API_KEY` | Dispara alerta no Telegram |

## Deploy sugerido

- **Railway / Render**: subir como worker, comando `python -m collector.main`
- **VPS**: rodar com `systemd` ou `pm2`
- **Local**: roda quando o computador está ligado (o webhook do Telegram e o dashboard continuam 24/7 no Lovable)
