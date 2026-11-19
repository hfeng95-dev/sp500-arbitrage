# S&P 500 Arbitrage & Reconstitution Engine — Project Handover Document

## 1. Executive Summary

The **S&P 500 Arbitrage & Reconstitution Engine** is a quantitative research and event-driven arbitrage platform designed to:
1. **Forecast S&P 500 Additions & Deletions**: Screens eligible S&P MidCap 400 and large-cap non-index stocks against official S&P Dow Jones Indices (S&P DJI) criteria while flagging vulnerable S&P 500 constituents (M&A takeovers or bottom-tier market-cap erosion + GAAP losses).
2. **Track NYSE Reconstitution Schedules**: Computes exact NYSE business-day cutoff dates, first-Friday announcements (5:15 PM ET), third-Friday MOC effective dates (adjusted for US market holidays such as Juneteenth/Good Friday), a 5-day `POST_EFFECTIVE` cooldown stage, and strictly monotonic `0–100%` cycle progress using `America/New_York` dates.
3. **Audit Historical Performance Honestly**: Runs a 3-year (13-quarter, `Q3 2023`–`Q3 2026`) point-in-time evaluation enforcing `validate_dataset_integrity()` (zero membership or state-transition contradictions), era-accurate S&P DJI market-cap thresholds, Precision@K & MRR alongside Recall@K, explicit small-pool saturation caveats, and expanding-window walk-forward out-of-sample validation.

---

## 2. Directory Structure & Key Modules

The project is located at: `/Users/hfeng/Work/Pythons/sp500_arbitrage`

```text
sp500_arbitrage/
├── app.py                 # Interactive Streamlit Web Application (Port 8502+)
├── data_loader.py         # Point-in-Time Historical Dataset (13 Quarters), Live Pools & Integrity Validator
├── sp500_engine.py        # S&P DJI Eligibility & Multi-Factor Ranking / Deletion Risk Engine
├── historic_evaluator.py  # Independent Evaluator, Precision@K/MRR & Expanding-Window Walk-Forward Auditor
├── timeline_manager.py    # NYSE Holiday-Aware Reconstitution Calendar & Milestone Engine
├── requirements.txt       # Self-contained dependencies (streamlit, pandas, watchdog)
├── run.sh                 # POSIX-safe macOS/Linux launcher (local .venv + hash-gated pip sync)
├── run.bat                # Windows launcher (local .venv + hash-gated pip sync + auto-open)
├── pytest.ini             # Pytest configuration
├── tests/                 # Automated unit & integrity test suite
│   ├── test_timeline.py
│   ├── test_engine.py
│   └── test_data_integrity.py
├── HANDOVER.md            # This handover document
├── README.md              # Quickstart guide
└── .gitignore             # Python, venv, cache, and test exclusions
```

### Module Specifications

| Module | Key Functions & Classes | Purpose |
| :--- | :--- | :--- |
| [`timeline_manager.py`](file:///Users/hfeng/Work/Pythons/sp500_arbitrage/timeline_manager.py) | `RebalanceTimelineManager`, `get_month_end()`, `get_nyse_holidays()`, `count_trading_days()` | Calculates quarterly schedules using `America/New_York` dates, NYSE holiday-aware month-end cutoffs, holiday-adjusted effective dates, true announcement-to-effective trading days, 5-day `POST_EFFECTIVE` cooldown, and strictly monotonic `0–100%` progress. |
| [`data_loader.py`](file:///Users/hfeng/Work/Pythons/sp500_arbitrage/data_loader.py) | `validate_dataset_integrity()`, `get_point_in_time_data()`, `get_historical_rebalances()`, `get_current_universe()` | Stores 13 quarters of curated point-in-time historical pools (`Q3 2023`–`Q3 2026`) and strictly non-overlapping live Q4 2026 pools with verified `S&P MidCap 400` vs `Non-Index / Large` feeder labels. Enforces zero double-additions, zero double-deletions, and zero stale-pool contamination. |
| [`sp500_engine.py`](file:///Users/hfeng/Work/Pythons/sp500_arbitrage/sp500_engine.py) | `SP500RebalanceEngine` | Official S&P DJI rules (`$22.7B` default / era lookup `$14.5B–$22.7B`, FMC `>= 50%` threshold, IWF `>= 0.10`, 6m min monthly volume `>= 250k`, 12m IPO seasoning, trailing 4Q GAAP sum `> 0` AND `Q0 > 0`, fail-closed missing core fields), true `math.log` market-cap scaling, unified `35/35/15/15` weights, and calibrated deletion risk scoring (`rank_bottom` + cap ratio + GAAP losses, reaching `HIGH RISK >= 75` up to `95.0`). |
| [`historic_evaluator.py`](file:///Users/hfeng/Work/Pythons/sp500_arbitrage/historic_evaluator.py) | `HistoricArbitrageEvaluator` | Audits all 13 quarters with era-accurate thresholds, `None`-safe date checks, Recall@3/5/10, Precision@3/5, MRR, dataset integrity integration, transparent small-pool caveats, and expanding-window walk-forward out-of-sample validation. |
| [`app.py`](file:///Users/hfeng/Work/Pythons/sp500_arbitrage/app.py) | Streamlit UI | Cached (`@st.cache_data`) dark-glassmorphism dashboard with escaped HTML/dollar signs (`&#36;` to prevent KaTeX mangling), dynamic badges, deterministic sorted filters, safe lookups, and `width="stretch"` tables. |

---

## 3. S&P Dow Jones Methodology & Scoring Model

### Unified Multi-Factor Weights (`SP500RebalanceEngine.DEFAULT_WEIGHTS`)
* **Market Capitalization (`35%`)**: True log-scaled score normalized from the era threshold up to `$150B`:
  `40 + 60 * log(mkt_cap / threshold) / log(150.0 / threshold)` (clamped to `[40, 100]`).
* **Feeder Preference (`35%`)**: `100` pts for `S&P MidCap 400` members vs `70` pts for `Non-Index / Large`.
* **Liquidity Turnover (`15%`)**: Annual dollar value traded / float-adjusted market cap (`>= 0.75` mandatory, fail-closed if missing).
* **Sector Representation (`15%`)**: Sector deficit priority multiplier (`0.80x`–`1.20x`).

### Era-Accurate Unadjusted Market-Cap Thresholds
* `2023`: `$14.5B`
* `H1 2024 (Q1–Q2 2024)`: `$15.8B`
* `H2 2024 (Q3–Q4 2024)`: `$18.0B`
* `H1 2025 (Q1–Q2 2025)`: `$20.5B`
* `H2 2025+ (Q3 2025 onward, default)`: `$22.7B`

### Deletion Vulnerability Scoring
1. **Pending M&A Takeovers (`98.0 CERTAIN`)**: Definitive mergers closing around rebalance dates (e.g., `K` / Kellanova acquired by Mars Inc. in live pool; `CTLT`, `DFS`, `HES`, `MRO`, `JNPR`, `X` historically).
2. **Organic Vulnerability (up to `95.0`)**: Weighted combination of:
   - `50%` Cap ratio (`mkt_cap_b / era_threshold`)
   - `25%` S&P 500 bottom rank (`rank_bottom`)
   - `25%` Consecutive negative GAAP quarters (`neg_earnings_streak`)
   Genuine distressed constituents (`< $7.5B`, bottom rank, sustained GAAP losses) properly reach `HIGH RISK (>= 75.0)` up to `95.0`.

---

## 4. Honest Evaluation & Walk-Forward Audit Results (13 Quarters)

Using canonical `DEFAULT_WEIGHTS` (`35/35/15/15`) and era-accurate thresholds across `Q3 2023`–`Q3 2026`:
* **Dataset Integrity**: `PASSED` (`0` membership/chronology errors across all 13 historical quarters + live pools).
* **Default Full-Sample Metrics (`35/35/15/15`)**:
  - Composite Rating: `8.8 / 10`
  - Additions: `Recall@3 = 57.9%`, `Recall@5 = 78.9%`, `Precision@5 = 46.2%`, `MRR = 0.490`
  - Deletions: `Recall@3 = 68.4%`, `Recall@5 = 94.7%`, `Precision@5 = 55.4%`, `MRR = 0.559`
* **Expanding-Window Walk-Forward Out-of-Sample Validation (9 OOS folds, 4-quarter warm-up)**:
  - OOS Avg Score: `8.8 / 10` | OOS Add `Recall@5 = 84.3%` | OOS Add `Precision@5 = 51.1%` | OOS Add `MRR = 0.441`
* **Small-Pool Caveat**: Curated PIT pools average `7.7` addition contenders and `5.3` deletion contenders per quarter. Because `pool_size <= 10` for additions (and `<= 5` in 9/13 deletion quarters), `Top-10` addition recall (`100%`) and some `Top-5` deletion recalls are pool-saturated. Always evaluate ranking quality using **Precision@K** and **MRR** alongside Recall@K.

---

## 5. How to Run & Verify

### Launch Web Dashboard
```bash
cd /Users/hfeng/Work/Pythons/sp500_arbitrage
./run.sh
```
On Windows, double-click or execute `run.bat`. Both scripts create/activate local `.venv`, sync `requirements.txt` only when its SHA-256 hash changes, and probe for a free port starting at `8502`.

### Run Automated Verification & CLI Audit
```bash
cd /Users/hfeng/Work/Pythons/sp500_arbitrage
.venv/bin/python -m py_compile *.py
.venv/bin/pytest -v
.venv/bin/python historic_evaluator.py
```
