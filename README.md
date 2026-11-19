# S&P 500 Arbitrage & Reconstitution Prediction Platform

An institutional-grade quantitative forecasting and event-driven arbitrage platform for S&P 500 quarterly reconstitutions.

## Features
- **S&P DJI Predictive Ranking Engine (`sp500_engine.py`)**: Implements official S&P Dow Jones Indices criteria:
  - Era-accurate unadjusted market-cap guidelines (`$14.5B` in 2023, `$15.8B` in H1 2024, `$18.0B` in H2 2024, `$20.5B` in H1 2025, `$22.7B` default from Jul 2025).
  - Float-Adjusted Market Cap (`FMC >= 50%` of threshold), Investable Weight Factor (`IWF >= 0.10`), 6-month minimum monthly trading volume (`>= 250,000` shares), and 12-month IPO seasoning (`>= 12` months).
  - Financial viability: trailing 4-quarter sum of GAAP net income `> 0` **AND** most recent quarter (`Q0`) `> 0`, with fail-closed defaults on missing core eligibility fields.
  - Unified multi-factor weights (`35%` log-scaled market cap / `35%` MidCap 400 feeder / `15%` liquidity / `15%` sector representation) and calibrated deletion risk scoring (`rank_bottom` + cap ratio + GAAP loss streak).
- **NYSE Calendar & Milestone Engine (`timeline_manager.py`)**: Uses `America/New_York` dates, NYSE holiday-aware month-end cutoffs, 5-day `POST_EFFECTIVE` cooldown window, true trading-day counts (handling Juneteenth/Good Friday), and strictly monotonic `0–100%` cycle progress.
- **Honest Point-in-Time Evaluator (`historic_evaluator.py`)**: Audits 13 quarters (`Q3 2023` – `Q3 2026`) with `validate_dataset_integrity()` (zero membership contradictions), Precision@K, MRR, Recall@K, transparent small-pool caveats, and expanding-window walk-forward out-of-sample validation.
- **Interactive Web Dashboard (`app.py`)**: Dark glassmorphic Streamlit dashboard on port `8502` (auto-probing free ports).

## Quick Start

### macOS / Linux
```bash
cd /Users/hfeng/Work/Pythons/sp500_arbitrage
./run.sh
```

### Windows
```bat
run.bat
```

### CLI Evaluator & Test Suite
```bash
.venv/bin/python historic_evaluator.py
.venv/bin/pytest -v
```

For full methodology, data integrity details, and historical scorecard output, see [HANDOVER.md](HANDOVER.md).
