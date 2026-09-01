"""
main.py

Orchestrates the daily digest pipeline against the LIVE Naira Sentiment
API:
1. Fetch recent headlines
2. Score each one via POST /analyze on the real API (bullish/bearish/noise)
3. Build a 2-minute digest
4. Check for a statistically significant shift in bearish rate vs. the
   previous period
5. Push notifications — daily digest, plus a high-priority alert if a
   significant shift is detected

Requires NAIRA_API_KEY to be set (sign up at
https://naira-sentiment-api-1.onrender.com/docs via POST /signup).
"""

import json
import os
from datetime import datetime, UTC
from dotenv import load_dotenv

loaded = load_dotenv()
print(f"load_dotenv() found a file: {loaded}")
def _mask_api_key(key: str) -> str:
    if not key or len(key) < 8:
        return "***"
    return f"{key[:8]}...{key[-4:]}"
NAIRA_API_KEY = os.getenv("NAIRA_API_KEY")

print(f"NAIRA_API_KEY loaded: {_mask_api_key(NAIRA_API_KEY)}")

from digest.data_source import fetch_recent_texts
from digest.naira_api_client import analyze_batch
from digest.digest import build_digest
from digest.shift_detector import detect_shift
from digest.notify import send_daily_digest, send_shift_alert

BASELINE_PATH = "artifacts/baseline_breakdown.json"


def load_baseline() -> dict:
    if os.path.exists(BASELINE_PATH):
        with open(BASELINE_PATH) as f:
            return json.load(f)
    return {"bullish": 0, "noise": 0, "bearish": 0}


def save_baseline(breakdown: dict):
    os.makedirs("artifacts", exist_ok=True)
    with open(BASELINE_PATH, "w") as f:
        json.dump(breakdown, f, indent=2)


def main():
    print(f"Running Naira Sentiment digest pipeline - {datetime.now(UTC).isoformat()}")

    print("Fetching recent headlines...")
    texts = fetch_recent_texts(hours_back=24, n_samples=15)

    print(f"Scoring {len(texts)} items via live Naira Sentiment API...")
    analyzed = analyze_batch(texts)

    print("Building digest...")
    digest = build_digest(analyzed)
    print(digest["summary_text"])

    print("Checking for significant sentiment shift vs. previous period...")
    baseline_breakdown = load_baseline()
    shift = detect_shift(digest["sentiment_breakdown"], baseline_breakdown)
    write_html_report(digest, shift)
    print(f"Shift check: {shift}")

    print("Sending daily digest notification...")
    send_daily_digest(digest)

    if shift["significant_shift"]:
        print("Significant shift detected - sending alert.")
        send_shift_alert(shift)
    else:
        print("No significant shift detected.")

    save_baseline(digest["sentiment_breakdown"])
    print("Pipeline complete.")


if __name__ == "__main__":
    main()

def write_html_report(digest: dict, shift: dict) -> None:
    os.makedirs("docs", exist_ok=True)
    timestamp = datetime.now(UTC).isoformat()
    summary_html = digest["summary_text"].replace("\n", "<br>")
    shift_line = (
        f"⚠️ Significant shift detected ({shift['direction']})"
        if shift["significant_shift"]
        else "No significant shift detected."
    )
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Naira Sentiment Digest</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: -apple-system, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; line-height: 1.5; }}
    h1 {{ font-size: 1.4rem; }}
    .meta {{ color: #666; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Naira Sentiment Digest</h1>
  <p class="meta">Last updated: {timestamp}</p>
  <p>{summary_html}</p>
  <p>{shift_line}</p>
</body>
</html>"""
    with open("docs/index.html", "w") as f:
        f.write(html)