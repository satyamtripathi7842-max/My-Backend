"""
notification/telegram.py
Sends alert messages to a Telegram chat via a bot.
Configure via environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""

import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_telegram_alert(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[telegram] Bot not configured — skipping send. Set TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as exc:
        print(f"[telegram] Failed to send alert: {exc}")
        return False
