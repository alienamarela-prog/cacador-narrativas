import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))
TOP_N_TOKENS = int(os.environ.get("TOP_N_TOKENS", "50"))
ALERT_THRESHOLD = float(os.environ.get("ALERT_THRESHOLD", "80"))
ALERT_COOLDOWN_MINUTES = int(os.environ.get("ALERT_COOLDOWN_MINUTES", "60"))
COINGECKO_BASE = os.environ.get("COINGECKO_BASE", "https://api.coingecko.com/api/v3")

RUN_ONCE = os.environ.get("RUN_ONCE", "false").lower() == "true"
