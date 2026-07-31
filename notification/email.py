"""
notification/email.py
Sends alert emails via SMTP. Configure via environment variables:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL_FROM
"""

import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", SMTP_USER)


def send_alert_email(to_address: str, subject: str, body: str) -> bool:
    """Returns True on success, False otherwise. Fails silently-logged if SMTP not configured."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[email] SMTP not configured — skipping send. Set SMTP_USER/SMTP_PASSWORD.")
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL_FROM
    msg["To"] = to_address

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(ALERT_EMAIL_FROM, [to_address], msg.as_string())
        return True
    except Exception as exc:
        print(f"[email] Failed to send alert email: {exc}")
        return False
