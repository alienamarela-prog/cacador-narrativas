from typing import Optional
import httpx
from .config import LOVABLE_BASE_URL, INGEST_API_KEY

HEADERS = {
    "Authorization": f"Bearer {INGEST_API_KEY}",
    "Content-Type": "application/json",
}

async def push_scores(scores: list[dict]):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{LOVABLE_BASE_URL}/api/public/ingest/scores",
                         headers=HEADERS, json={"scores": scores})
        r.raise_for_status()
        return r.json()

async def trigger_alert(*, token: str, symbol: str, score: float, level: str,
                         title: str, body: str, meta: Optional[dict] = None):
    payload = {"token": token, "symbol": symbol, "score": score, "level": level,
               "title": title, "body": body, "meta": meta or {}}
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{LOVABLE_BASE_URL}/api/public/alerts/trigger",
                         headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()
