"""
data_source.py

Pulls recent Nigerian financial headlines to feed into the live sentiment
API. This is a mock/stub — the sentiment SCORING is real (your live
Naira Sentiment API), but the text SOURCE here is placeholder headlines.
Swap this out for a real feed (news API, RSS, social listening) once
you're ready to go from "demo" to "actually monitoring live news."
"""

from datetime import datetime, timedelta
import random

SAMPLE_HEADLINES = [
    "Naira strengthens against dollar as CBN intervenes in forex market",
    "Fuel scarcity worsens in Lagos as marketers hoard petrol",
    "Nigerian stock exchange records strong gains this week",
    "Inflation rate climbs to new high, food prices surge",
    "CBN raises interest rates in bid to tame inflation",
    "Tech startups in Lagos attract record funding this quarter",
    "Naira depreciates further amid dollar scarcity",
    "Government announces new fiscal policy to boost manufacturing",
    "Banks report strong Q3 earnings despite economic headwinds",
    "Rising diesel costs squeeze transport and logistics sector",
]


def fetch_recent_texts(hours_back: int = 24, n_samples: int = 15) -> list[dict]:
    """
    Returns a list of {"text": str, "timestamp": datetime, "source": str}.
    Kept small (n_samples=15 by default) since each item is a real API
    call against your free-tier rate limits — raise this once you're on
    a paid tier or have your own rate-limit headroom confirmed.
    """
    now = datetime.utcnow()
    texts = []
    for _ in range(n_samples):
        texts.append({
            "text": random.choice(SAMPLE_HEADLINES),
            "timestamp": now - timedelta(hours=random.uniform(0, hours_back)),
            "source": "mock_feed",
        })
    return texts