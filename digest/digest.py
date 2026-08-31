"""
digest.py

Builds a short, readable daily digest from analyzed sentiment data —
using the real label set from the Naira Sentiment API: bullish, bearish,
noise. Designed to be read in under two minutes.
"""

from collections import Counter

LABELS = ["bullish", "bearish", "noise"]


def build_digest(analyzed_texts: list[dict]) -> dict:
    if not analyzed_texts:
        return {"summary_text": "No data available for this period.", "total_items": 0}

    labels = [item["sentiment_label"] for item in analyzed_texts]
    breakdown = dict(Counter(labels))
    for label in LABELS:
        breakdown.setdefault(label, 0)

    dominant = max(breakdown, key=breakdown.get)

    bearish_items = sorted(
        [i for i in analyzed_texts if i["sentiment_label"] == "bearish"],
        key=lambda x: x["timestamp"],
        reverse=True,
    )[:3]
    bullish_items = sorted(
        [i for i in analyzed_texts if i["sentiment_label"] == "bullish"],
        key=lambda x: x["timestamp"],
        reverse=True,
    )[:3]

    total = len(analyzed_texts)
    summary_lines = [
        f"Naira sentiment digest — {total} items analyzed.",
        f"Overall lean: {dominant.upper()} "
        f"({breakdown['bullish']} bullish, {breakdown['noise']} noise, {breakdown['bearish']} bearish).",
    ]
    if bearish_items:
        summary_lines.append("Bearish signals:")
        for item in bearish_items:
            summary_lines.append(f"  - {item['text']}")
    if bullish_items:
        summary_lines.append("Bullish signals:")
        for item in bullish_items:
            summary_lines.append(f"  - {item['text']}")

    return {
        "total_items": total,
        "sentiment_breakdown": breakdown,
        "dominant_sentiment": dominant,
        "bearish_headlines": [i["text"] for i in bearish_items],
        "bullish_headlines": [i["text"] for i in bullish_items],
        "summary_text": "\n".join(summary_lines),
    }