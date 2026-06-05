"""Plugue aqui sua fonte de menções sociais (X/Twitter, Reddit, Farcaster).
Por padrão retorna stub neutro — o score ainda funciona com base em volume e price action."""
from typing import Dict

async def fetch_social_signals(symbols: list[str]) -> Dict[str, dict]:
    return {s: {"mentions": 0, "sentiment": 0.0} for s in symbols}
