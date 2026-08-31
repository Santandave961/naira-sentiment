"""
test_pipeline.py

Offline tests for the digest and shift-detection logic — these don't
call the live API at all, so they can run anywhere, anytime, and prove
the pipeline's actual reasoning is correct independent of network access
or API key availability.

Run with:
    python test_pipeline.py
"""

from datetime import datetime, timedelta, UTC
from digest.digest import build_digest
from digest.shift_detector import detect_shift


def make_item(text, label, hours_ago=1):
    return {
        "text": text,
        "timestamp": datetime.now(UTC) - timedelta(hours=hours_ago),
        "source": "test",
        "sentiment_label": label,
    }


def test_digest_basic_breakdown():
    items = [
        make_item("Naira strengthens against dollar", "bullish"),
        make_item("Fuel scarcity worsens", "bearish"),
        make_item("Fuel scarcity worsens", "bearish"),
        make_item("Market stable today", "noise"),
    ]
    digest = build_digest(items)

    assert digest["total_items"] == 4
    assert digest["sentiment_breakdown"]["bearish"] == 2
    assert digest["sentiment_breakdown"]["bullish"] == 1
    assert digest["sentiment_breakdown"]["noise"] == 1
    assert digest["dominant_sentiment"] == "bearish"
    assert "Fuel scarcity worsens" in digest["bearish_headlines"]
    print("PASS: test_digest_basic_breakdown")


def test_digest_empty_input():
    digest = build_digest([])
    assert digest["total_items"] == 0
    assert "No data" in digest["summary_text"]
    print("PASS: test_digest_empty_input")


def test_shift_detector_no_shift_when_similar():
    current = {"bullish": 20, "noise": 20, "bearish": 10}
    baseline = {"bullish": 22, "noise": 18, "bearish": 10}
    result = detect_shift(current, baseline)
    assert result["significant_shift"] is False
    assert result["direction"] == "stable"
    print("PASS: test_shift_detector_no_shift_when_similar")


def test_shift_detector_detects_worsening():
    # Bearish rate jumps from 10% to 60% — should clearly trigger
    current = {"bullish": 20, "noise": 20, "bearish": 60}
    baseline = {"bullish": 45, "noise": 45, "bearish": 10}
    result = detect_shift(current, baseline)
    assert result["significant_shift"] is True
    assert result["direction"] == "worsening"
    assert result["z_score"] > 0
    print("PASS: test_shift_detector_detects_worsening")


def test_shift_detector_detects_improving():
    # Bearish rate drops from 60% to 10% — should trigger, opposite direction
    current = {"bullish": 45, "noise": 45, "bearish": 10}
    baseline = {"bullish": 20, "noise": 20, "bearish": 60}
    result = detect_shift(current, baseline)
    assert result["significant_shift"] is True
    assert result["direction"] == "improving"
    assert result["z_score"] < 0
    print("PASS: test_shift_detector_detects_improving")


def test_shift_detector_handles_empty_baseline():
    # First-ever run — no prior baseline. Should not crash or false-trigger.
    current = {"bullish": 10, "noise": 5, "bearish": 5}
    baseline = {"bullish": 0, "noise": 0, "bearish": 0}
    result = detect_shift(current, baseline)
    assert result["significant_shift"] is False
    print("PASS: test_shift_detector_handles_empty_baseline")


def run_all():
    tests = [
        test_digest_basic_breakdown,
        test_digest_empty_input,
        test_shift_detector_no_shift_when_similar,
        test_shift_detector_detects_worsening,
        test_shift_detector_detects_improving,
        test_shift_detector_handles_empty_baseline,
    ]
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"FAIL: {test.__name__} — {e}")
            failed += 1

    print(f"\n{len(tests) - failed}/{len(tests)} tests passed.")
    if failed:
        exit(1)


if __name__ == "__main__":
    run_all()