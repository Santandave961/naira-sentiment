# Naira Sentiment Digest

A fully automated daily pipeline that fetches recent Naira financial headlines, scores their sentiment via a live sentiment API, builds a readable digest, detects statistically significant shifts vs. the previous period, and pushes notifications — all on a scheduled cron, with a public, auto-updating status page.

**Live digest:** https://santandave961.github.io/naira-sentiment/

## What it does

1. Fetches recent Naira-related financial headlines
2. Scores each one via a live sentiment API (bullish / bearish / noise)
3. Builds a short, readable daily digest summarizing the overall lean and key signals
4. Checks for a statistically significant shift in bearish rate vs. the previous period
5. Sends push notifications — a daily digest, plus a high-priority alert if a significant shift is detected
6. Publishes the latest digest to a public GitHub Pages site

## Architecture

```
main.py                        # Orchestrates the full pipeline
digest/
  data_source.py               # Fetches recent headlines
  naira_api_client.py          # Calls the live sentiment API, maps labels
  digest.py                    # Builds the digest summary + breakdown
  shift_detector.py            # Statistical shift detection vs. baseline
  notify.py                    # Sends push notifications via ntfy.sh
artifacts/
  baseline_breakdown.json      # Yesterday's sentiment breakdown (persisted)
docs/
  index.html                   # Auto-generated public status page
.github/workflows/
  daily-digest.yml             # Scheduled CI pipeline (daily cron)
test_pipeline.py               # Offline tests, no live API calls
```

## How it runs

A GitHub Actions workflow runs daily at 7 AM UTC (and can be triggered manually):

1. Checks out the repo and installs dependencies
2. Runs offline tests
3. Runs the full pipeline against the live API
4. Commits the updated baseline and public HTML report back to the repo
5. GitHub Pages serves the latest digest from `docs/`

## Setup

Requires a `NAIRA_API_KEY` (sign up via `POST /signup` on the sentiment API) and an `NTFY_TOPIC` for push notifications via [ntfy.sh](https://ntfy.sh) — a free, no-signup notification service. Subscribe to the topic in the ntfy app or browser to receive alerts.

```bash
pip install -r requirements.txt
```

Set environment variables locally in a `.env` file:
```
NAIRA_API_KEY=your_key_here
NTFY_TOPIC=your_topic_here
```

Run the pipeline:
```bash
python main.py
```

Run offline tests (no live API calls):
```bash
python test_pipeline.py
```

In CI, both variables are stored as GitHub Actions repository secrets rather than committed to the repo.

## Who this helps

- **Individual traders/investors** — instead of manually scrolling naira financial headlines every morning trying to gauge market mood, get a 2-minute digest with the overall lean and the specific headlines driving it.
- **Small businesses trading in or exposed to naira** — early, automated warning when sentiment shifts significantly (e.g. worsening bearish signals), so pricing, procurement, or FX decisions aren't made on stale intuition.
- **Analysts/researchers** — a running, auditable history of daily sentiment breakdowns (committed to the repo) that can be tracked over time without manually logging anything.
- **Anyone who wants signal without noise** — the pipeline explicitly filters out neutral/irrelevant headlines ("noise") so only genuinely bullish or bearish signals surface in the digest.

The core value is time and attention: turning a manual, subjective morning ritual into a reliable, automated, glanceable daily habit — delivered as a push notification rather than something you have to remember to check.

## Design notes

- **Label mapping**: the live API returns `positive` / `negative` / `neutral`; the pipeline maps these to `bullish` / `bearish` / `noise` internally.
- **Retry with backoff**: API calls retry on timeouts, connection errors, and 5xx responses (not on 4xx, which won't self-resolve), with exponential backoff.
- **Baseline persistence**: rather than relying on GitHub Actions cache (not guaranteed to persist), the pipeline commits the updated baseline straight back to the repo after each run, giving a durable, auditable history of sentiment breakdowns over time.
- **Shift detection**: compares today's bearish rate against the previous baseline using a z-score test, flagging significant shifts and their direction (worsening / improving).

## Background

Built by [Wisdom](https://github.com/Santandave961) — a self-taught data scientist and ML engineer with a background in accounting. The debugging process behind this pipeline (label mismatches, dead code, CI caching quirks, cold-start timeouts) mirrors the same discrepancy-tracing discipline used in reconciling ledgers: don't trust the first explanation, follow it until it actually closes.
