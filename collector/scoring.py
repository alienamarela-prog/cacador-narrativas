from typing import Optional
import math

def narrative_score(*, price_change_24h: Optional[float], volume_24h: Optional[float],
                    market_cap: Optional[float], mentions: int, sentiment: float) -> float:
    """Score 0-100. Combina momentum + liquidez + buzz social."""
    pct = price_change_24h or 0.0
    momentum = max(-30, min(30, pct))
    vol_score = 0.0
    if volume_24h and market_cap:
        ratio = volume_24h / max(market_cap, 1)
        vol_score = min(30, math.log10(max(ratio, 1e-4) * 1000 + 1) * 10)
    social = min(40, math.log10(mentions + 1) * 12 + sentiment * 10)
    raw = momentum + vol_score + social + 30
    return round(max(0.0, min(100.0, raw)), 2)
