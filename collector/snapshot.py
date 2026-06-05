import json
from pathlib import Path
from datetime import datetime, timezone

SNAPSHOT_PATH = Path("data/latest_snapshot.json")

def _limpar_para_json(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        if isinstance(obj, dict):
            return {k: _limpar_para_json(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_limpar_para_json(v) for v in obj]
        return str(obj)

def salvar_snapshot(
    *,
    ranking,
    alpha_hunter,
    alien_research,
    narrative_dex,
    explosoes,
    tokens_mercado=None,
):
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "ranking": _limpar_para_json(ranking),
        "alpha_hunter": _limpar_para_json(alpha_hunter),
        "alien_research": _limpar_para_json(alien_research),
        "narrative_dex": _limpar_para_json(narrative_dex),
        "explosoes": _limpar_para_json(explosoes),
        "tokens_mercado": _limpar_para_json(tokens_mercado or []),
    }

    SNAPSHOT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload
