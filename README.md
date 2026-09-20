# S&P 500 Arbitrage & Reconstitution Prediction Platform

An institutional-grade quantitative forecasting and event-driven arbitrage platform for S&P 500 quarterly reconstitutions.

## Features
- **Predictive Ranking Engine**: Implements the official S&P Dow Jones Indices (S&P DJI) 7-point methodology (Market Cap threshold, 4Q cumulative GAAP earnings, liquidity turnover, S&P MidCap 400 feeder preference).
- **Timeline & Milestone Engine**: Real-time cycle tracker for Data Cutoff Dates, Official S&P Announcements, and Market-on-Close (MOC) Effective Dates.
- **Zero Future Leakage Evaluator**: 3-year point-in-time historical backtest (13 consecutive quarters from Q3 2023 through Q3 2026) with zero lookahead bias (`Cutoff < Announcement < Effective`).
- **Interactive Web Dashboard**: Modern dark glassmorphic Streamlit interface on port 8502.

## Quick Start
```bash
./run.sh
```
Access the application at `http://localhost:8502`.

To run the automated 13-quarter audit CLI:
```bash
python historic_evaluator.py
```

For complete technical documentation, methodology formulas, and case studies, refer to [HANDOVER.md](HANDOVER.md).
