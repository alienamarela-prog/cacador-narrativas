STABLE_SYMBOLS = {
    "USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDD", "USDE", "USD1",
    "PYUSD", "GUSD", "LUSD", "FRAX", "SUSD", "USDP", "EURC", "EURS"
}

WRAPPED_SYMBOLS = {
    "WETH", "WBTC", "WBNB", "WSOL", "STETH", "RETH", "CBETH"
}

BLOCKED_SYMBOLS = STABLE_SYMBOLS | WRAPPED_SYMBOLS

def is_allowed_token(token: dict) -> bool:
    symbol = str(token.get("symbol", "")).upper()
    name = str(token.get("name", "")).lower()
    market_cap = token.get("market_cap") or 0
    volume = token.get("total_volume") or 0

    if symbol in BLOCKED_SYMBOLS:
        return False

    if "wrapped" in name:
        return False

    if "bridged" in name:
        return False

    if "usd" in name and symbol not in {"HYPE", "SUI"}:
        return False

    if market_cap <= 0 or volume <= 0:
        return False

    return True
