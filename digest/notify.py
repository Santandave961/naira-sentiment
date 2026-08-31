"""
notify.py

Sends push notifications for the daily digest and significant shift
alerts, via ntfy.sh (free, no signup — pick a unique topic and subscribe
to it in the ntfy app or browser).
"""

import os
import requests

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "naira-sentiment-digest-demo")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


def _ascii_safe(text: str) -> str:
    """HTTP headers must be ASCII-safe — strip characters like em-dashes
    or emoji that would otherwise break the request."""
    return text.encode("ascii", errors="ignore").decode("ascii").strip()


def send_notification(title: str, message: str, priority: str = "default") -> bool:
    try:
        response = requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            headers={"Title": _ascii_safe(title), "Priority": priority},
            timeout=10,
        )
        response.raise_for_status()
        print(f"Notification sent to topic '{NTFY_TOPIC}': {title}")
        return True
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return False


def send_daily_digest(digest: dict):
    send_notification(
        title=f"Naira Sentiment Digest - {digest['dominant_sentiment'].upper()}",
        message=digest["summary_text"],
        priority="default",
    )


def send_shift_alert(shift: dict):
    direction_label = "Improving" if shift["direction"] == "improving" else "Worsening"
    send_notification(
        title=f"Sentiment Shift Alert - {direction_label}",
        message=(
            f"Bearish rate moved from {shift['baseline_bearish_rate']:.0%} "
            f"to {shift['current_bearish_rate']:.0%} (z={shift['z_score']}). "
            f"Statistically significant shift."
        ),
        priority="high",
    )