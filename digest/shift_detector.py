"""
shift_detector.py

Detects a statistically significant shift in the BEARISH rate between two
periods — this is what triggers "alert when sentiment shifts
significantly." Uses a two-proportion z-test, the same approach as the
A/B Testing Framework project.
"""

import math


def _proportion_z_test(count1, n1, count2, n2) -> float:
    if n1 == 0 or n2 == 0:
        return 0.0
    p1 = count1 / n1
    p2 = count2 / n2
    p_pool = (count1 + count2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0
    return (p1 - p2) / se


def detect_shift(current_breakdown: dict, baseline_breakdown: dict, z_threshold: float = 1.96) -> dict:
    """
    Compares the bearish rate between current and baseline periods.
    z_threshold=1.96 = 95% confidence level.
    """
    current_total = sum(current_breakdown.values())
    baseline_total = sum(baseline_breakdown.values())

    current_bearish = current_breakdown.get("bearish", 0)
    baseline_bearish = baseline_breakdown.get("bearish", 0)

    z = _proportion_z_test(current_bearish, current_total, baseline_bearish, baseline_total)

    significant = abs(z) >= z_threshold
    if not significant:
        direction = "stable"
    elif z > 0:
        direction = "worsening"  # bearish rate went up
    else:
        direction = "improving"  # bearish rate went down

    return {
        "significant_shift": significant,
        "z_score": round(z, 3),
        "current_bearish_rate": round(current_bearish / current_total, 3) if current_total else 0,
        "baseline_bearish_rate": round(baseline_bearish / baseline_total, 3) if baseline_total else 0,
        "direction": direction,
    }