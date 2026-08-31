"""
naira_api_client.py

Client for the live Naira Sentiment API (naira-sentiment-api-1.onrender.com).

Contract (confirmed from /docs):
    POST /analyze
    Header: x-api-key: <your key>
    Body:   {"text": "<headline or text to score>"}
    Response: a sentiment label string — "bullish", "bearish", or "noise"

Get an API key by POSTing to /signup first (see README). Free tier is
rate-limited; this client is written to be gentle about that (small
delay between calls, clear error surfacing rather than silent retries).
"""

import os
import time
import requests
import time

BASE_URL = os.getenv("NAIRA_API_BASE_URL", "https://naira-sentiment-api-1.onrender.com")
API_KEY = os.getenv("NAIRA_API_KEY")

ANALYZE_ENDPOINT = f"{BASE_URL}/analyze"

# Free-tier Render instances sleep when idle — first request can be slow
# to wake the service up. Give it a generous timeout.
REQUEST_TIMEOUT = 60
DELAY_BETWEEN_CALLS = 0.5  # be gentle on the free tier / rate limits
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # exponential backoff: 1s,


def analyze_text(text: str) -> str:
    """
    Sends a single piece of text to the live Naira Sentiment API and
    returns the sentiment label: "bullish", "bearish", or "noise".

    Raises requests.HTTPError if the API key is missing/invalid, or if
    the request otherwise fails — callers should let this surface loudly
    rather than silently treating a failed call as "noise".
    """
    if not API_KEY:
        raise RuntimeError(
            "NAIRA_API_KEY is not set. Sign up at "
            f"{BASE_URL}/docs (POST /signup) to get a key, then set it "
            "as an environment variable."
        )

    last_error = None
    response = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                ANALYZE_ENDPOINT,
                headers={"x-api-key": API_KEY},
                json={"text": text},
                timeout=REQUEST_TIMEOUT,
            )
    
            response.raise_for_status()
            break # success

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF_BASE ** attempt
                print(f" Attempt {attempt} failed ({type(e).__name__}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"analyze_text failed after {MAX_RETRIES} attempts: {last_error}") from e

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status is not None and 500 <= status < 600 and attempt < MAX_RETRIES:
                last_error = e
                wait = RETRY_BACKOFF_BASE ** attempt
                print(f" Attempt {attempt} failed (HTTP {status}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise #4xx, or out of retries on a 5xx: fail loudly

    result = response.json()

    # Per the API's documented response schema, this returns a plain
    # JSON string, e.g. "bullish" — not an object
    if isinstance(result, str):
        label = result
    elif isinstance(result, dict):
        for key in ("label", "sentiment", "result", "prediction", "sentiment_label", "class"):
            if key in result:
                label = result[key]
                break
        else:
            raise RuntimeError(
                f"Unrecognized response shape from /analyze - got a dict"
                f"but none of the expected keys were found. Raw response: {result}."
                "Update naira_api_client.py's analyze_text() with the correct key."
            )
    else:
        raise RuntimeError(f"Unexpected response type from /analyze: {type(result)} - {result}")



    label = str(label).strip().lower()
    label_map = {
        "positive": "bullish",
        "negative": "bearish",
        "neutral": "noise",
        "mixed": "noise",
    }
    label = label_map.get(label, "noise")  # default to noise if unrecognized

    return label


def analyze_batch(texts: list[dict]) -> list[dict]:
    """
    Takes a list of {"text", "timestamp", "source"} dicts (from
    data_source.py) and returns the same list with "sentiment_label"
    added, using the real Naira Sentiment API.
    """
    results = []
    for i, item in enumerate(texts):
        label = analyze_text(item["text"])
        print(f"DEBUG label={label!r}")
        results.append({**item, "sentiment_label": label})

        if i < len(texts) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)

    return results