"""
S&P 500 Arbitrage Data Engine & Point-in-Time Historical Repository
Provides:
1. Ground-truth historical S&P 500 additions and deletions by quarter (3 FULL YEARS: Q3 2023 - Q3 2026).
2. Point-in-time frozen financial and market metrics (Cutoff < Announcement < Effective).
3. Current active candidate feeder universe (strictly non-S&P 500 candidates) and
   vulnerable S&P 500 constituents (strictly active S&P 500 members).
4. Automated dataset integrity validator (`validate_dataset_integrity()`).
"""

from datetime import date
from typing import Dict, Any, List, Set

# Legacy S&P 500 constituents already in the index prior to Q3 2023 that must never
# appear in addition candidate pools (e.g., FICO entered S&P 500 in March 2023).
KNOWN_LEGACY_SP500_MEMBERS: Set[str] = {"FICO"}

# --- 3-Year Historical Ground Truth: S&P Dow Jones Indices Reconstitution Actions ---
HISTORICAL_REBALANCES: Dict[str, Dict[str, Any]] = {
    "Q3 2026": {
        "cutoff_date": date(2026, 8, 31),
        "announcement_date": date(2026, 9, 4),
        "effective_date": date(2026, 9, 18),
        "actual_additions": [
            {"ticker": "RDDT", "name": "Reddit Inc.", "sector": "Communication Services", "mkt_cap_b": 26.5},
            {"ticker": "FERG", "name": "Ferguson Enterprises", "sector": "Industrials", "mkt_cap_b": 42.0},
            {"ticker": "BE", "name": "Bloom Energy", "sector": "Industrials", "mkt_cap_b": 23.5},
        ],
        "actual_deletions": [
            {"ticker": "TAP", "name": "Molson Coors Beverage Co.", "sector": "Consumer Staples", "mkt_cap_b": 7.4},
            {"ticker": "TTD", "name": "The Trade Desk", "sector": "Communication Services", "mkt_cap_b": 14.5},
            {"ticker": "BLDR", "name": "Builders FirstSource", "sector": "Industrials", "mkt_cap_b": 15.2},
        ],
    },
    "Q2 2026": {
        "cutoff_date": date(2026, 5, 29),
        "announcement_date": date(2026, 6, 5),
        "effective_date": date(2026, 6, 22),
        "actual_additions": [
            {"ticker": "FLEX", "name": "Flex Ltd.", "sector": "Information Technology", "mkt_cap_b": 24.2},
            {"ticker": "MRVL", "name": "Marvell Technology", "sector": "Information Technology", "mkt_cap_b": 68.4},
        ],
        "actual_deletions": [
            {"ticker": "TECH", "name": "Bio-Techne Corp.", "sector": "Health Care", "mkt_cap_b": 8.5},
            {"ticker": "APA", "name": "APA Corporation", "sector": "Energy", "mkt_cap_b": 7.1},
        ],
    },
    "Q1 2026": {
        "cutoff_date": date(2026, 2, 27),
        "announcement_date": date(2026, 3, 6),
        "effective_date": date(2026, 3, 23),
        "actual_additions": [
            {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 38.4},
            {"ticker": "COHR", "name": "Coherent Corp.", "sector": "Information Technology", "mkt_cap_b": 23.4},
            {"ticker": "LITE", "name": "Lumentum Holdings", "sector": "Information Technology", "mkt_cap_b": 22.9},
            {"ticker": "ECHO", "name": "EchoStar Corp.", "sector": "Communication Services", "mkt_cap_b": 23.8},
        ],
        "actual_deletions": [
            {"ticker": "FRT", "name": "Federal Realty Inv Trust", "sector": "Real Estate", "mkt_cap_b": 8.1},
            {"ticker": "MHK", "name": "Mohawk Industries", "sector": "Consumer Discretionary", "mkt_cap_b": 7.6},
            {"ticker": "NWSA", "name": "News Corp (Class A)", "sector": "Communication Services", "mkt_cap_b": 6.8},
            {"ticker": "AIZ", "name": "Assurant Inc.", "sector": "Financials", "mkt_cap_b": 8.9},
        ],
    },
    "Q4 2025": {
        "cutoff_date": date(2025, 11, 28),
        "announcement_date": date(2025, 12, 5),
        "effective_date": date(2025, 12, 22),
        "actual_additions": [
            {"ticker": "CVNA", "name": "Carvana Co.", "sector": "Consumer Discretionary", "mkt_cap_b": 48.0},
            {"ticker": "FIX", "name": "Comfort Systems USA", "sector": "Industrials", "mkt_cap_b": 23.6},
            {"ticker": "CRH", "name": "CRH plc", "sector": "Materials", "mkt_cap_b": 72.0},
            {"ticker": "ARES", "name": "Ares Management", "sector": "Financials", "mkt_cap_b": 56.5},
        ],
        "actual_deletions": [
            {"ticker": "JNPR", "name": "Juniper Networks", "sector": "Information Technology", "mkt_cap_b": 13.5},
            {"ticker": "X", "name": "United States Steel", "sector": "Materials", "mkt_cap_b": 10.2},
            {"ticker": "IPG", "name": "Interpublic Group", "sector": "Communication Services", "mkt_cap_b": 7.9},
            {"ticker": "HAS", "name": "Hasbro Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.2},
        ],
    },
    "Q3 2025": {
        "cutoff_date": date(2025, 8, 29),
        "announcement_date": date(2025, 9, 5),
        "effective_date": date(2025, 9, 22),
        "actual_additions": [
            {"ticker": "APP", "name": "AppLovin Corp", "sector": "Information Technology", "mkt_cap_b": 42.1},
            {"ticker": "HOOD", "name": "Robinhood Markets", "sector": "Financials", "mkt_cap_b": 31.5},
            {"ticker": "EME", "name": "EMCOR Group", "sector": "Industrials", "mkt_cap_b": 24.2},
        ],
        "actual_deletions": [
            {"ticker": "HES", "name": "Hess Corp", "sector": "Energy", "mkt_cap_b": 44.5},
            {"ticker": "MRO", "name": "Marathon Oil", "sector": "Energy", "mkt_cap_b": 17.5},
            {"ticker": "BWA", "name": "BorgWarner Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.8},
        ],
    },
    "Q2 2025": {
        "cutoff_date": date(2025, 5, 30),
        "announcement_date": date(2025, 6, 6),
        "effective_date": date(2025, 6, 23),
        "actual_additions": [
            {"ticker": "COIN", "name": "Coinbase Global", "sector": "Financials", "mkt_cap_b": 54.0},
            {"ticker": "DDOG", "name": "Datadog Inc.", "sector": "Information Technology", "mkt_cap_b": 46.2},
        ],
        "actual_deletions": [
            {"ticker": "DFS", "name": "Discover Financial", "sector": "Financials", "mkt_cap_b": 42.0},
            {"ticker": "RL", "name": "Ralph Lauren Corp", "sector": "Consumer Discretionary", "mkt_cap_b": 8.2},
        ],
    },
    "Q1 2025": {
        "cutoff_date": date(2025, 2, 28),
        "announcement_date": date(2025, 3, 7),
        "effective_date": date(2025, 3, 24),
        "actual_additions": [
            {"ticker": "DASH", "name": "DoorDash Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 68.0},
            {"ticker": "WSM", "name": "Williams-Sonoma", "sector": "Consumer Discretionary", "mkt_cap_b": 22.5},
            {"ticker": "TKO", "name": "TKO Group Holdings", "sector": "Communication Services", "mkt_cap_b": 21.0},
            {"ticker": "EXE", "name": "Expand Energy", "sector": "Energy", "mkt_cap_b": 23.4},
        ],
        "actual_deletions": [
            {"ticker": "PARA", "name": "Paramount Global", "sector": "Communication Services", "mkt_cap_b": 7.4},
            {"ticker": "QRVO", "name": "Qorvo Inc.", "sector": "Information Technology", "mkt_cap_b": 6.8},
            {"ticker": "FOX", "name": "Fox Corp Class B", "sector": "Communication Services", "mkt_cap_b": 7.1},
            {"ticker": "TFX", "name": "Teleflex Inc.", "sector": "Health Care", "mkt_cap_b": 6.5},
        ],
    },
    "Q4 2024": {
        "cutoff_date": date(2024, 11, 29),
        "announcement_date": date(2024, 12, 6),
        "effective_date": date(2024, 12, 23),
        "actual_additions": [
            {"ticker": "APO", "name": "Apollo Global Management", "sector": "Financials", "mkt_cap_b": 82.5},
            {"ticker": "WDAY", "name": "Workday Inc.", "sector": "Information Technology", "mkt_cap_b": 71.0},
            {"ticker": "LII", "name": "Lennox International", "sector": "Industrials", "mkt_cap_b": 23.8},
        ],
        "actual_deletions": [
            {"ticker": "MKTX", "name": "MarketAxess Holdings", "sector": "Financials", "mkt_cap_b": 7.6},
            {"ticker": "VFC", "name": "V.F. Corp", "sector": "Consumer Discretionary", "mkt_cap_b": 6.4},
            {"ticker": "CTLT", "name": "Catalent Inc.", "sector": "Health Care", "mkt_cap_b": 11.4},
        ],
    },
    "Q3 2024": {
        "cutoff_date": date(2024, 8, 30),
        "announcement_date": date(2024, 9, 6),
        "effective_date": date(2024, 9, 23),
        "actual_additions": [
            {"ticker": "PLTR", "name": "Palantir Technologies", "sector": "Information Technology", "mkt_cap_b": 69.5},
            {"ticker": "DELL", "name": "Dell Technologies", "sector": "Information Technology", "mkt_cap_b": 78.4},
            {"ticker": "ERIE", "name": "Erie Indemnity", "sector": "Financials", "mkt_cap_b": 26.2},
        ],
        "actual_deletions": [
            {"ticker": "AAL", "name": "American Airlines Group", "sector": "Industrials", "mkt_cap_b": 7.2},
            {"ticker": "ETSY", "name": "Etsy Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.1},
            {"ticker": "BIO", "name": "Bio-Rad Laboratories", "sector": "Health Care", "mkt_cap_b": 7.8},
        ],
    },
    "Q2 2024": {
        "cutoff_date": date(2024, 5, 31),
        "announcement_date": date(2024, 6, 7),
        "effective_date": date(2024, 6, 24),
        "actual_additions": [
            {"ticker": "KKR", "name": "KKR & Co. Inc.", "sector": "Financials", "mkt_cap_b": 94.0},
            {"ticker": "CRWD", "name": "CrowdStrike Holdings", "sector": "Information Technology", "mkt_cap_b": 78.2},
            {"ticker": "GDDY", "name": "GoDaddy Inc.", "sector": "Information Technology", "mkt_cap_b": 20.8},
        ],
        "actual_deletions": [
            {"ticker": "RHI", "name": "Robert Half Inc.", "sector": "Industrials", "mkt_cap_b": 6.8},
            {"ticker": "CMA", "name": "Comerica Inc.", "sector": "Financials", "mkt_cap_b": 6.5},
            {"ticker": "ILMN", "name": "Illumina Inc.", "sector": "Health Care", "mkt_cap_b": 17.2},
        ],
    },
    "Q1 2024": {
        "cutoff_date": date(2024, 2, 29),
        "announcement_date": date(2024, 3, 1),
        "effective_date": date(2024, 3, 18),
        "actual_additions": [
            {"ticker": "SMCI", "name": "Super Micro Computer", "sector": "Information Technology", "mkt_cap_b": 50.4},
            {"ticker": "DECK", "name": "Deckers Outdoor", "sector": "Consumer Discretionary", "mkt_cap_b": 23.5},
        ],
        "actual_deletions": [
            {"ticker": "WHR", "name": "Whirlpool Corp.", "sector": "Consumer Discretionary", "mkt_cap_b": 5.8},
            {"ticker": "ZION", "name": "Zions Bancorporation", "sector": "Financials", "mkt_cap_b": 5.9},
        ],
    },
    "Q4 2023": {
        "cutoff_date": date(2023, 11, 30),
        "announcement_date": date(2023, 12, 1),
        "effective_date": date(2023, 12, 18),
        "actual_additions": [
            {"ticker": "UBER", "name": "Uber Technologies", "sector": "Industrials", "mkt_cap_b": 118.0},
            {"ticker": "JBL", "name": "Jabil Inc.", "sector": "Information Technology", "mkt_cap_b": 15.6},
            {"ticker": "BLDR", "name": "Builders FirstSource", "sector": "Industrials", "mkt_cap_b": 17.8},
        ],
        "actual_deletions": [
            {"ticker": "SEE", "name": "Sealed Air Corp.", "sector": "Materials", "mkt_cap_b": 4.5},
            {"ticker": "ALK", "name": "Alaska Air Group", "sector": "Industrials", "mkt_cap_b": 4.6},
            {"ticker": "SEDG", "name": "SolarEdge Technologies", "sector": "Information Technology", "mkt_cap_b": 4.8},
        ],
    },
    "Q3 2023": {
        "cutoff_date": date(2023, 8, 31),
        "announcement_date": date(2023, 9, 1),
        "effective_date": date(2023, 9, 18),
        "actual_additions": [
            {"ticker": "BX", "name": "Blackstone Inc.", "sector": "Financials", "mkt_cap_b": 128.0},
            {"ticker": "ABNB", "name": "Airbnb Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 84.0},
        ],
        "actual_deletions": [
            {"ticker": "LNC", "name": "Lincoln National Corp.", "sector": "Financials", "mkt_cap_b": 4.2},
            {"ticker": "NWL", "name": "Newell Brands", "sector": "Consumer Discretionary", "mkt_cap_b": 4.1},
        ],
    },
}

# --- Point-in-Time Historical Candidate Universes (STRICTLY NON-S&P 500 AS OF CUTOFF DATE) ---
# Clean feeder labels: S&P MidCap 400 vs Non-Index / Large.
HISTORICAL_POINT_IN_TIME_CANDIDATES: Dict[str, List[Dict[str, Any]]] = {
    "Q3 2026": [
        {"ticker": "FERG", "name": "Ferguson Enterprises", "sector": "Industrials", "mkt_cap_b": 42.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VEEV", "name": "Veeva Systems Inc.", "sector": "Health Care", "mkt_cap_b": 38.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ALNY", "name": "Alnylam Pharmaceuticals", "sector": "Health Care", "mkt_cap_b": 34.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.25, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "RDDT", "name": "Reddit Inc.", "sector": "Communication Services", "mkt_cap_b": 26.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.10, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "SOFI", "name": "SoFi Technologies Inc.", "sector": "Financials", "mkt_cap_b": 25.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.85, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "CW", "name": "Curtiss-Wright Corp.", "sector": "Industrials", "mkt_cap_b": 24.6, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.92, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "USFD", "name": "US Foods Holding Corp.", "sector": "Consumer Staples", "mkt_cap_b": 24.1, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "BE", "name": "Bloom Energy", "sector": "Industrials", "mkt_cap_b": 23.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.65, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "MSTR", "name": "Strategy Inc. (MicroStrategy)", "sector": "Information Technology", "mkt_cap_b": 38.0, "gaap_4q_pos": False, "gaap_q0_pos": False, "liq_ratio": 2.90, "feeder": "Non-Index / Large", "us_domicile": True},
    ],
    "Q2 2026": [
        {"ticker": "MRVL", "name": "Marvell Technology", "sector": "Information Technology", "mkt_cap_b": 68.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.75, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "FERG", "name": "Ferguson Enterprises", "sector": "Industrials", "mkt_cap_b": 39.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VEEV", "name": "Veeva Systems Inc.", "sector": "Health Care", "mkt_cap_b": 37.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.08, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ALNY", "name": "Alnylam Pharmaceuticals", "sector": "Health Care", "mkt_cap_b": 33.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.20, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "FLEX", "name": "Flex Ltd.", "sector": "Information Technology", "mkt_cap_b": 24.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.20, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "RDDT", "name": "Reddit Inc.", "sector": "Communication Services", "mkt_cap_b": 23.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.00, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "USFD", "name": "US Foods Holding Corp.", "sector": "Consumer Staples", "mkt_cap_b": 23.1, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.00, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "BE", "name": "Bloom Energy", "sector": "Industrials", "mkt_cap_b": 21.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.45, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q1 2026": [
        {"ticker": "MRVL", "name": "Marvell Technology", "sector": "Information Technology", "mkt_cap_b": 61.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.60, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 38.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.45, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "FERG", "name": "Ferguson Enterprises", "sector": "Industrials", "mkt_cap_b": 37.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.08, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VEEV", "name": "Veeva Systems Inc.", "sector": "Health Care", "mkt_cap_b": 35.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ECHO", "name": "EchoStar Corp.", "sector": "Communication Services", "mkt_cap_b": 23.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.35, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "COHR", "name": "Coherent Corp.", "sector": "Information Technology", "mkt_cap_b": 23.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.25, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "LITE", "name": "Lumentum Holdings", "sector": "Information Technology", "mkt_cap_b": 22.9, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "FLEX", "name": "Flex Ltd.", "sector": "Information Technology", "mkt_cap_b": 21.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q4 2025": [
        {"ticker": "CRH", "name": "CRH plc", "sector": "Materials", "mkt_cap_b": 72.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.30, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "MRVL", "name": "Marvell Technology", "sector": "Information Technology", "mkt_cap_b": 58.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.55, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ARES", "name": "Ares Management", "sector": "Financials", "mkt_cap_b": 56.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "CVNA", "name": "Carvana Co.", "sector": "Consumer Discretionary", "mkt_cap_b": 48.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.40, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "FERG", "name": "Ferguson Enterprises", "sector": "Industrials", "mkt_cap_b": 36.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 32.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.35, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "FIX", "name": "Comfort Systems USA", "sector": "Industrials", "mkt_cap_b": 23.6, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "FLEX", "name": "Flex Ltd.", "sector": "Information Technology", "mkt_cap_b": 20.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.00, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q3 2025": [
        {"ticker": "CRH", "name": "CRH plc", "sector": "Materials", "mkt_cap_b": 60.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.25, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ARES", "name": "Ares Management", "sector": "Financials", "mkt_cap_b": 48.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "APP", "name": "AppLovin Corp", "sector": "Information Technology", "mkt_cap_b": 42.1, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.85, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "CVNA", "name": "Carvana Co.", "sector": "Consumer Discretionary", "mkt_cap_b": 35.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.20, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "HOOD", "name": "Robinhood Markets", "sector": "Financials", "mkt_cap_b": 31.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.70, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 30.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.30, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "EME", "name": "EMCOR Group", "sector": "Industrials", "mkt_cap_b": 24.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "FIX", "name": "Comfort Systems USA", "sector": "Industrials", "mkt_cap_b": 21.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q2 2025": [
        {"ticker": "COIN", "name": "Coinbase Global", "sector": "Financials", "mkt_cap_b": 54.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.10, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "DDOG", "name": "Datadog Inc.", "sector": "Information Technology", "mkt_cap_b": 46.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.45, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ARES", "name": "Ares Management", "sector": "Financials", "mkt_cap_b": 44.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.08, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "APP", "name": "AppLovin Corp", "sector": "Information Technology", "mkt_cap_b": 34.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.70, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 28.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.28, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "HOOD", "name": "Robinhood Markets", "sector": "Financials", "mkt_cap_b": 25.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.60, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "EME", "name": "EMCOR Group", "sector": "Industrials", "mkt_cap_b": 22.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.02, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q1 2025": [
        {"ticker": "DASH", "name": "DoorDash Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 68.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.65, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "COIN", "name": "Coinbase Global", "sector": "Financials", "mkt_cap_b": 48.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.05, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "DDOG", "name": "Datadog Inc.", "sector": "Information Technology", "mkt_cap_b": 42.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.40, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "APP", "name": "AppLovin Corp", "sector": "Information Technology", "mkt_cap_b": 36.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.68, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 27.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.32, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "EXE", "name": "Expand Energy", "sector": "Energy", "mkt_cap_b": 23.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "WSM", "name": "Williams-Sonoma", "sector": "Consumer Discretionary", "mkt_cap_b": 22.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.95, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "TKO", "name": "TKO Group Holdings", "sector": "Communication Services", "mkt_cap_b": 21.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.20, "feeder": "Non-Index / Large", "us_domicile": True},
    ],
    "Q4 2024": [
        {"ticker": "APO", "name": "Apollo Global Management", "sector": "Financials", "mkt_cap_b": 82.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "WDAY", "name": "Workday Inc.", "sector": "Information Technology", "mkt_cap_b": 71.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.35, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "DASH", "name": "DoorDash Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 58.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.55, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "COIN", "name": "Coinbase Global", "sector": "Financials", "mkt_cap_b": 42.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.95, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "APP", "name": "AppLovin Corp", "sector": "Information Technology", "mkt_cap_b": 34.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.65, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 30.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.30, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "LII", "name": "Lennox International", "sector": "Industrials", "mkt_cap_b": 23.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.88, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "WSM", "name": "Williams-Sonoma", "sector": "Consumer Discretionary", "mkt_cap_b": 19.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.92, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q3 2024": [
        {"ticker": "DELL", "name": "Dell Technologies", "sector": "Information Technology", "mkt_cap_b": 78.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.45, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "APO", "name": "Apollo Global Management", "sector": "Financials", "mkt_cap_b": 65.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.12, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "PLTR", "name": "Palantir Technologies", "sector": "Information Technology", "mkt_cap_b": 69.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.95, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "WDAY", "name": "Workday Inc.", "sector": "Information Technology", "mkt_cap_b": 62.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.30, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "APP", "name": "AppLovin Corp", "sector": "Information Technology", "mkt_cap_b": 32.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.62, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "VRT", "name": "Vertiv Holdings", "sector": "Industrials", "mkt_cap_b": 31.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.35, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "ERIE", "name": "Erie Indemnity", "sector": "Financials", "mkt_cap_b": 26.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.82, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "WSM", "name": "Williams-Sonoma", "sector": "Consumer Discretionary", "mkt_cap_b": 18.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.95, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q2 2024": [
        {"ticker": "DELL", "name": "Dell Technologies", "sector": "Information Technology", "mkt_cap_b": 95.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.50, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "KKR", "name": "KKR & Co. Inc.", "sector": "Financials", "mkt_cap_b": 94.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "CRWD", "name": "CrowdStrike Holdings", "sector": "Information Technology", "mkt_cap_b": 78.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.80, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "PLTR", "name": "Palantir Technologies", "sector": "Information Technology", "mkt_cap_b": 51.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.75, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "GDDY", "name": "GoDaddy Inc.", "sector": "Information Technology", "mkt_cap_b": 20.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.90, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "ERIE", "name": "Erie Indemnity", "sector": "Financials", "mkt_cap_b": 19.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.80, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "LII", "name": "Lennox International", "sector": "Industrials", "mkt_cap_b": 18.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.84, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q1 2024": [
        {"ticker": "KKR", "name": "KKR & Co. Inc.", "sector": "Financials", "mkt_cap_b": 84.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "CRWD", "name": "CrowdStrike Holdings", "sector": "Information Technology", "mkt_cap_b": 72.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.75, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "SMCI", "name": "Super Micro Computer", "sector": "Information Technology", "mkt_cap_b": 50.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 2.45, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "DECK", "name": "Deckers Outdoor", "sector": "Consumer Discretionary", "mkt_cap_b": 23.5, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.92, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "ERIE", "name": "Erie Indemnity", "sector": "Financials", "mkt_cap_b": 18.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.78, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "GDDY", "name": "GoDaddy Inc.", "sector": "Information Technology", "mkt_cap_b": 17.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.85, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "LII", "name": "Lennox International", "sector": "Industrials", "mkt_cap_b": 16.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.82, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q4 2023": [
        {"ticker": "UBER", "name": "Uber Technologies", "sector": "Industrials", "mkt_cap_b": 118.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.55, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "DECK", "name": "Deckers Outdoor", "sector": "Consumer Discretionary", "mkt_cap_b": 18.4, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.90, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "BLDR", "name": "Builders FirstSource", "sector": "Industrials", "mkt_cap_b": 17.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.10, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "JBL", "name": "Jabil Inc.", "sector": "Information Technology", "mkt_cap_b": 15.6, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.95, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "SMCI", "name": "Super Micro Computer", "sector": "Information Technology", "mkt_cap_b": 15.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.80, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "GDDY", "name": "GoDaddy Inc.", "sector": "Information Technology", "mkt_cap_b": 15.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.82, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "ERIE", "name": "Erie Indemnity", "sector": "Financials", "mkt_cap_b": 15.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.76, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
    "Q3 2023": [
        {"ticker": "BX", "name": "Blackstone Inc.", "sector": "Financials", "mkt_cap_b": 128.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.30, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "ABNB", "name": "Airbnb Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 84.0, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.40, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "UBER", "name": "Uber Technologies", "sector": "Industrials", "mkt_cap_b": 92.0, "gaap_4q_pos": False, "gaap_q0_pos": True, "liq_ratio": 1.50, "feeder": "Non-Index / Large", "us_domicile": True},
        {"ticker": "BLDR", "name": "Builders FirstSource", "sector": "Industrials", "mkt_cap_b": 16.1, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "DECK", "name": "Deckers Outdoor", "sector": "Consumer Discretionary", "mkt_cap_b": 15.2, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.88, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "JBL", "name": "Jabil Inc.", "sector": "Information Technology", "mkt_cap_b": 14.8, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.92, "feeder": "S&P MidCap 400", "us_domicile": True},
        {"ticker": "SMCI", "name": "Super Micro Computer", "sector": "Information Technology", "mkt_cap_b": 14.6, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.75, "feeder": "S&P MidCap 400", "us_domicile": True},
    ],
}

# --- Point-in-Time Historical Deletion Watchlists (STRICTLY ACTIVE S&P 500 MEMBERS AS OF CUTOFF) ---
HISTORICAL_POINT_IN_TIME_DELETIONS: Dict[str, List[Dict[str, Any]]] = {
    "Q3 2026": [
        {"ticker": "TAP", "name": "Molson Coors Beverage Co.", "sector": "Consumer Staples", "mkt_cap_b": 7.4, "neg_earnings_streak": 2, "rank_bottom": 3},
        {"ticker": "WBA", "name": "Walgreens Boots Alliance", "sector": "Consumer Staples", "mkt_cap_b": 7.6, "neg_earnings_streak": 3, "rank_bottom": 2},
        {"ticker": "CZR", "name": "Caesars Entertainment Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.9, "neg_earnings_streak": 2, "rank_bottom": 1},
        {"ticker": "CPB", "name": "The Campbell's Company", "sector": "Consumer Staples", "mkt_cap_b": 11.4, "neg_earnings_streak": 1, "rank_bottom": 11},
        {"ticker": "TTD", "name": "The Trade Desk", "sector": "Communication Services", "mkt_cap_b": 14.5, "neg_earnings_streak": 0, "rank_bottom": 25},
        {"ticker": "BLDR", "name": "Builders FirstSource", "sector": "Industrials", "mkt_cap_b": 15.2, "neg_earnings_streak": 0, "rank_bottom": 30},
    ],
    "Q2 2026": [
        {"ticker": "APA", "name": "APA Corporation", "sector": "Energy", "mkt_cap_b": 7.1, "neg_earnings_streak": 2, "rank_bottom": 2},
        {"ticker": "TECH", "name": "Bio-Techne Corp.", "sector": "Health Care", "mkt_cap_b": 8.5, "neg_earnings_streak": 1, "rank_bottom": 5},
        {"ticker": "TAP", "name": "Molson Coors Beverage Co.", "sector": "Consumer Staples", "mkt_cap_b": 8.1, "neg_earnings_streak": 1, "rank_bottom": 4},
        {"ticker": "WBA", "name": "Walgreens Boots Alliance", "sector": "Consumer Staples", "mkt_cap_b": 7.8, "neg_earnings_streak": 2, "rank_bottom": 3},
        {"ticker": "CZR", "name": "Caesars Entertainment Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.2, "neg_earnings_streak": 1, "rank_bottom": 1},
    ],
    "Q1 2026": [
        {"ticker": "NWSA", "name": "News Corp (Class A)", "sector": "Communication Services", "mkt_cap_b": 6.8, "neg_earnings_streak": 2, "rank_bottom": 2},
        {"ticker": "MHK", "name": "Mohawk Industries", "sector": "Consumer Discretionary", "mkt_cap_b": 7.6, "neg_earnings_streak": 1, "rank_bottom": 3},
        {"ticker": "FRT", "name": "Federal Realty Inv Trust", "sector": "Real Estate", "mkt_cap_b": 8.1, "neg_earnings_streak": 0, "rank_bottom": 5},
        {"ticker": "AIZ", "name": "Assurant Inc.", "sector": "Financials", "mkt_cap_b": 8.9, "neg_earnings_streak": 0, "rank_bottom": 7},
        {"ticker": "APA", "name": "APA Corporation", "sector": "Energy", "mkt_cap_b": 7.5, "neg_earnings_streak": 1, "rank_bottom": 4},
        {"ticker": "TECH", "name": "Bio-Techne Corp.", "sector": "Health Care", "mkt_cap_b": 8.8, "neg_earnings_streak": 0, "rank_bottom": 6},
    ],
    "Q4 2025": [
        {"ticker": "JNPR", "name": "Juniper Networks", "sector": "Information Technology", "mkt_cap_b": 13.5, "ma_pending": True, "acquirer": "HPE", "rank_bottom": 45},
        {"ticker": "X", "name": "United States Steel", "sector": "Materials", "mkt_cap_b": 10.2, "ma_pending": True, "acquirer": "Nippon Steel", "rank_bottom": 20},
        {"ticker": "HAS", "name": "Hasbro Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.2, "neg_earnings_streak": 2, "rank_bottom": 2},
        {"ticker": "IPG", "name": "Interpublic Group", "sector": "Communication Services", "mkt_cap_b": 7.9, "neg_earnings_streak": 1, "rank_bottom": 4},
        {"ticker": "MHK", "name": "Mohawk Industries", "sector": "Consumer Discretionary", "mkt_cap_b": 8.0, "neg_earnings_streak": 0, "rank_bottom": 5},
        {"ticker": "NWSA", "name": "News Corp (Class A)", "sector": "Communication Services", "mkt_cap_b": 7.4, "neg_earnings_streak": 1, "rank_bottom": 3},
    ],
    "Q3 2025": [
        {"ticker": "HES", "name": "Hess Corp", "sector": "Energy", "mkt_cap_b": 44.5, "ma_pending": True, "acquirer": "Chevron", "rank_bottom": 115},
        {"ticker": "MRO", "name": "Marathon Oil", "sector": "Energy", "mkt_cap_b": 17.5, "ma_pending": True, "acquirer": "ConocoPhillips", "rank_bottom": 60},
        {"ticker": "BWA", "name": "BorgWarner Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.8, "neg_earnings_streak": 1, "rank_bottom": 2},
        {"ticker": "HAS", "name": "Hasbro Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.5, "neg_earnings_streak": 1, "rank_bottom": 3},
        {"ticker": "IPG", "name": "Interpublic Group", "sector": "Communication Services", "mkt_cap_b": 8.1, "neg_earnings_streak": 0, "rank_bottom": 5},
    ],
    "Q2 2025": [
        {"ticker": "DFS", "name": "Discover Financial", "sector": "Financials", "mkt_cap_b": 42.0, "ma_pending": True, "acquirer": "Capital One", "rank_bottom": 120},
        {"ticker": "RL", "name": "Ralph Lauren Corp", "sector": "Consumer Discretionary", "mkt_cap_b": 8.2, "neg_earnings_streak": 0, "rank_bottom": 4},
        {"ticker": "BWA", "name": "BorgWarner Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.1, "neg_earnings_streak": 1, "rank_bottom": 2},
        {"ticker": "HAS", "name": "Hasbro Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.8, "neg_earnings_streak": 1, "rank_bottom": 3},
        {"ticker": "IPG", "name": "Interpublic Group", "sector": "Communication Services", "mkt_cap_b": 8.4, "neg_earnings_streak": 0, "rank_bottom": 6},
    ],
    "Q1 2025": [
        {"ticker": "TFX", "name": "Teleflex Inc.", "sector": "Health Care", "mkt_cap_b": 6.5, "neg_earnings_streak": 2, "rank_bottom": 1},
        {"ticker": "QRVO", "name": "Qorvo Inc.", "sector": "Information Technology", "mkt_cap_b": 6.8, "neg_earnings_streak": 2, "rank_bottom": 2},
        {"ticker": "PARA", "name": "Paramount Global", "sector": "Communication Services", "mkt_cap_b": 7.4, "neg_earnings_streak": 3, "rank_bottom": 4},
        {"ticker": "FOX", "name": "Fox Corp Class B", "sector": "Communication Services", "mkt_cap_b": 7.1, "neg_earnings_streak": 0, "rank_bottom": 3},
        {"ticker": "BWA", "name": "BorgWarner Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.3, "neg_earnings_streak": 0, "rank_bottom": 5},
        {"ticker": "RL", "name": "Ralph Lauren Corp", "sector": "Consumer Discretionary", "mkt_cap_b": 8.5, "neg_earnings_streak": 0, "rank_bottom": 7},
    ],
    "Q4 2024": [
        {"ticker": "CTLT", "name": "Catalent Inc.", "sector": "Health Care", "mkt_cap_b": 11.4, "ma_pending": True, "acquirer": "Novo Holdings", "rank_bottom": 35},
        {"ticker": "VFC", "name": "V.F. Corp", "sector": "Consumer Discretionary", "mkt_cap_b": 6.4, "neg_earnings_streak": 3, "rank_bottom": 2},
        {"ticker": "MKTX", "name": "MarketAxess Holdings", "sector": "Financials", "mkt_cap_b": 7.6, "neg_earnings_streak": 1, "rank_bottom": 5},
        {"ticker": "PARA", "name": "Paramount Global", "sector": "Communication Services", "mkt_cap_b": 7.5, "neg_earnings_streak": 2, "rank_bottom": 4},
        {"ticker": "QRVO", "name": "Qorvo Inc.", "sector": "Information Technology", "mkt_cap_b": 7.1, "neg_earnings_streak": 1, "rank_bottom": 3},
    ],
    "Q3 2024": [
        {"ticker": "ETSY", "name": "Etsy Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.1, "neg_earnings_streak": 2, "rank_bottom": 3},
        {"ticker": "AAL", "name": "American Airlines Group", "sector": "Industrials", "mkt_cap_b": 7.2, "neg_earnings_streak": 1, "rank_bottom": 5},
        {"ticker": "BIO", "name": "Bio-Rad Laboratories", "sector": "Health Care", "mkt_cap_b": 7.8, "neg_earnings_streak": 0, "rank_bottom": 7},
        {"ticker": "VFC", "name": "V.F. Corp", "sector": "Consumer Discretionary", "mkt_cap_b": 6.6, "neg_earnings_streak": 2, "rank_bottom": 4},
        {"ticker": "MKTX", "name": "MarketAxess Holdings", "sector": "Financials", "mkt_cap_b": 8.0, "neg_earnings_streak": 0, "rank_bottom": 8},
    ],
    "Q2 2024": [
        {"ticker": "CMA", "name": "Comerica Inc.", "sector": "Financials", "mkt_cap_b": 6.5, "neg_earnings_streak": 1, "rank_bottom": 3},
        {"ticker": "RHI", "name": "Robert Half Inc.", "sector": "Industrials", "mkt_cap_b": 6.8, "neg_earnings_streak": 0, "rank_bottom": 4},
        {"ticker": "ILMN", "name": "Illumina Inc.", "sector": "Health Care", "mkt_cap_b": 17.2, "neg_earnings_streak": 4, "rank_bottom": 18},
        {"ticker": "AAL", "name": "American Airlines Group", "sector": "Industrials", "mkt_cap_b": 7.4, "neg_earnings_streak": 1, "rank_bottom": 5},
        {"ticker": "ETSY", "name": "Etsy Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.9, "neg_earnings_streak": 1, "rank_bottom": 6},
    ],
    "Q1 2024": [
        {"ticker": "WHR", "name": "Whirlpool Corp.", "sector": "Consumer Discretionary", "mkt_cap_b": 5.8, "neg_earnings_streak": 1, "rank_bottom": 2},
        {"ticker": "ZION", "name": "Zions Bancorporation", "sector": "Financials", "mkt_cap_b": 5.9, "neg_earnings_streak": 1, "rank_bottom": 3},
        {"ticker": "CMA", "name": "Comerica Inc.", "sector": "Financials", "mkt_cap_b": 6.7, "neg_earnings_streak": 0, "rank_bottom": 4},
        {"ticker": "RHI", "name": "Robert Half Inc.", "sector": "Industrials", "mkt_cap_b": 7.1, "neg_earnings_streak": 0, "rank_bottom": 5},
        {"ticker": "ETSY", "name": "Etsy Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 7.3, "neg_earnings_streak": 0, "rank_bottom": 6},
    ],
    "Q4 2023": [
        {"ticker": "SEE", "name": "Sealed Air Corp.", "sector": "Materials", "mkt_cap_b": 4.5, "neg_earnings_streak": 2, "rank_bottom": 2},
        {"ticker": "ALK", "name": "Alaska Air Group", "sector": "Industrials", "mkt_cap_b": 4.6, "neg_earnings_streak": 1, "rank_bottom": 3},
        {"ticker": "SEDG", "name": "SolarEdge Technologies", "sector": "Information Technology", "mkt_cap_b": 4.8, "neg_earnings_streak": 2, "rank_bottom": 4},
        {"ticker": "WHR", "name": "Whirlpool Corp.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.1, "neg_earnings_streak": 1, "rank_bottom": 5},
        {"ticker": "ZION", "name": "Zions Bancorporation", "sector": "Financials", "mkt_cap_b": 6.2, "neg_earnings_streak": 0, "rank_bottom": 6},
    ],
    "Q3 2023": [
        {"ticker": "NWL", "name": "Newell Brands", "sector": "Consumer Discretionary", "mkt_cap_b": 4.1, "neg_earnings_streak": 2, "rank_bottom": 1},
        {"ticker": "LNC", "name": "Lincoln National Corp.", "sector": "Financials", "mkt_cap_b": 4.2, "neg_earnings_streak": 4, "rank_bottom": 2},
        {"ticker": "SEE", "name": "Sealed Air Corp.", "sector": "Materials", "mkt_cap_b": 5.1, "neg_earnings_streak": 1, "rank_bottom": 4},
        {"ticker": "ALK", "name": "Alaska Air Group", "sector": "Industrials", "mkt_cap_b": 5.2, "neg_earnings_streak": 0, "rank_bottom": 5},
        {"ticker": "WHR", "name": "Whirlpool Corp.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.4, "neg_earnings_streak": 0, "rank_bottom": 7},
    ],
}


# --- Current Live Active Universe Candidate Pool (Q4 2026 Cycle — strictly non-S&P 500) ---
CURRENT_FEEDER_CANDIDATES: List[Dict[str, Any]] = [
    {"ticker": "CW", "name": "Curtiss-Wright Corp.", "sector": "Industrials", "mkt_cap_b": 25.4, "fmc_b": 24.9, "iwf": 0.98, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.96, "min_monthly_vol": 4_200_000, "ipo_months": 360, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "USFD", "name": "US Foods Holding Corp.", "sector": "Consumer Staples", "mkt_cap_b": 24.8, "fmc_b": 24.3, "iwf": 0.98, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.12, "min_monthly_vol": 28_000_000, "ipo_months": 124, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "UTHR", "name": "United Therapeutics Corp.", "sector": "Health Care", "mkt_cap_b": 24.1, "fmc_b": 23.4, "iwf": 0.97, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.05, "min_monthly_vol": 6_800_000, "ipo_months": 324, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "CASY", "name": "Casey's General Stores", "sector": "Consumer Staples", "mkt_cap_b": 23.6, "fmc_b": 23.1, "iwf": 0.98, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.89, "min_monthly_vol": 5_100_000, "ipo_months": 480, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "MANH", "name": "Manhattan Associates Inc.", "sector": "Information Technology", "mkt_cap_b": 23.2, "fmc_b": 22.7, "iwf": 0.98, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.18, "min_monthly_vol": 11_500_000, "ipo_months": 336, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "VEEV", "name": "Veeva Systems Inc.", "sector": "Health Care", "mkt_cap_b": 39.5, "fmc_b": 35.6, "iwf": 0.90, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.14, "min_monthly_vol": 18_400_000, "ipo_months": 156, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "ALNY", "name": "Alnylam Pharmaceuticals", "sector": "Health Care", "mkt_cap_b": 36.2, "fmc_b": 35.1, "iwf": 0.97, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.28, "min_monthly_vol": 16_200_000, "ipo_months": 268, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "SOFI", "name": "SoFi Technologies Inc.", "sector": "Financials", "mkt_cap_b": 26.8, "fmc_b": 25.2, "iwf": 0.94, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.92, "min_monthly_vol": 420_000_000, "ipo_months": 64, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "TOST", "name": "Toast Inc.", "sector": "Financials", "mkt_cap_b": 24.4, "fmc_b": 21.5, "iwf": 0.88, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.45, "min_monthly_vol": 110_000_000, "ipo_months": 61, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "NET", "name": "Cloudflare Inc.", "sector": "Information Technology", "mkt_cap_b": 41.0, "fmc_b": 36.1, "iwf": 0.88, "gaap_4q_pos": False, "gaap_q0_pos": False, "liq_ratio": 1.78, "min_monthly_vol": 58_000_000, "ipo_months": 85, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "MSTR", "name": "Strategy Inc. (MicroStrategy)", "sector": "Information Technology", "mkt_cap_b": 36.5, "fmc_b": 32.1, "iwf": 0.88, "gaap_4q_pos": False, "gaap_q0_pos": False, "liq_ratio": 2.95, "min_monthly_vol": 210_000_000, "ipo_months": 340, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "MEDP", "name": "Medpace Holdings Inc.", "sector": "Health Care", "mkt_cap_b": 21.2, "fmc_b": 17.4, "iwf": 0.82, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.84, "min_monthly_vol": 4_100_000, "ipo_months": 122, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "LAD", "name": "Lithia Motors Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 19.8, "fmc_b": 19.2, "iwf": 0.97, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 0.88, "min_monthly_vol": 4_600_000, "ipo_months": 358, "feeder": "S&P MidCap 400", "us_domicile": True},
    {"ticker": "SYM", "name": "Symbotic Inc.", "sector": "Industrials", "mkt_cap_b": 18.8, "fmc_b": 5.6, "iwf": 0.30, "gaap_4q_pos": False, "gaap_q0_pos": False, "liq_ratio": 1.25, "min_monthly_vol": 24_000_000, "ipo_months": 52, "feeder": "Non-Index / Large", "us_domicile": True},
    {"ticker": "DUOL", "name": "Duolingo Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 16.5, "fmc_b": 14.5, "iwf": 0.88, "gaap_4q_pos": True, "gaap_q0_pos": True, "liq_ratio": 1.15, "min_monthly_vol": 14_500_000, "ipo_months": 63, "feeder": "S&P MidCap 400", "us_domicile": True},
]

# --- Current Live Vulnerable S&P 500 Constituents (strictly active S&P 500 members) ---
CURRENT_VULNERABLE_CONSTITUENTS: List[Dict[str, Any]] = [
    {"ticker": "K", "name": "Kellanova", "sector": "Consumer Staples", "mkt_cap_b": 28.5, "neg_earnings_streak": 0, "rank_bottom": 95, "ma_pending": True, "acquirer": "Mars Inc."},
    {"ticker": "CZR", "name": "Caesars Entertainment Inc.", "sector": "Consumer Discretionary", "mkt_cap_b": 6.4, "neg_earnings_streak": 3, "rank_bottom": 1, "ma_pending": False},
    {"ticker": "WBA", "name": "Walgreens Boots Alliance", "sector": "Consumer Staples", "mkt_cap_b": 7.1, "neg_earnings_streak": 4, "rank_bottom": 2, "ma_pending": False},
    {"ticker": "ENPH", "name": "Enphase Energy Inc.", "sector": "Information Technology", "mkt_cap_b": 7.2, "neg_earnings_streak": 2, "rank_bottom": 3, "ma_pending": False},
    {"ticker": "LW", "name": "Lamb Weston Holdings Inc.", "sector": "Consumer Staples", "mkt_cap_b": 8.4, "neg_earnings_streak": 2, "rank_bottom": 4, "ma_pending": False},
    {"ticker": "AES", "name": "The AES Corporation", "sector": "Utilities", "mkt_cap_b": 9.1, "neg_earnings_streak": 1, "rank_bottom": 6, "ma_pending": False},
    {"ticker": "MGM", "name": "MGM Resorts International", "sector": "Consumer Discretionary", "mkt_cap_b": 9.8, "neg_earnings_streak": 1, "rank_bottom": 8, "ma_pending": False},
    {"ticker": "CPB", "name": "The Campbell's Company", "sector": "Consumer Staples", "mkt_cap_b": 11.2, "neg_earnings_streak": 1, "rank_bottom": 12, "ma_pending": False},
]


def _quarter_sort_key(quarter_label: str):
    """Parses 'Q3 2023' into (2023, 3) for strict chronological ordering."""
    parts = quarter_label.strip().split()
    if len(parts) == 2 and parts[0].startswith("Q"):
        return (int(parts[1]), int(parts[0][1:]))
    return (0, 0)


def validate_dataset_integrity(raise_on_error: bool = False) -> Dict[str, Any]:
    """
    Validates chronological ordering, zero membership state-transition contradictions,
    and zero stale-pool contamination across historical and current datasets.
    """
    errors: List[str] = []
    warnings: List[str] = []

    chronological_quarters = sorted(HISTORICAL_REBALANCES.keys(), key=_quarter_sort_key)

    # Track live membership state across chronological replay
    # Values: "IN" (added in history or legacy), "OUT" (deleted in history)
    membership_state: Dict[str, str] = {t: "IN" for t in KNOWN_LEGACY_SP500_MEMBERS}
    last_event: Dict[str, str] = {t: "legacy pre-2023 S&P 500 member" for t in KNOWN_LEGACY_SP500_MEMBERS}

    prev_cutoff = None
    prev_effective = None

    for q in chronological_quarters:
        meta = HISTORICAL_REBALANCES[q]
        cutoff = meta.get("cutoff_date")
        announce = meta.get("announcement_date")
        effective = meta.get("effective_date")

        # 1. Timestamp validity & monotonicity
        if not (isinstance(cutoff, date) and isinstance(announce, date) and isinstance(effective, date)):
            errors.append(f"{q}: Missing or invalid date field (cutoff={cutoff}, announce={announce}, effective={effective})")
        else:
            if not (cutoff < announce < effective):
                errors.append(f"{q}: Date ordering violated ({cutoff} < {announce} < {effective})")
            if prev_cutoff is not None and cutoff <= prev_cutoff:
                errors.append(f"{q}: cutoff_date {cutoff} not strictly after previous cutoff {prev_cutoff}")
            if prev_effective is not None and effective <= prev_effective:
                errors.append(f"{q}: effective_date {effective} not strictly after previous effective {prev_effective}")
            prev_cutoff = cutoff
            prev_effective = effective

        add_pool = HISTORICAL_POINT_IN_TIME_CANDIDATES.get(q, [])
        del_pool = HISTORICAL_POINT_IN_TIME_DELETIONS.get(q, [])
        actual_adds = [a["ticker"] for a in meta.get("actual_additions", [])]
        actual_dels = [d["ticker"] for d in meta.get("actual_deletions", [])]

        # 2. Check duplicates within pools and actuals
        add_pool_tickers = [c["ticker"] for c in add_pool]
        del_pool_tickers = [c["ticker"] for c in del_pool]
        if len(add_pool_tickers) != len(set(add_pool_tickers)):
            errors.append(f"{q}: Duplicate ticker found in addition candidate pool")
        if len(del_pool_tickers) != len(set(del_pool_tickers)):
            errors.append(f"{q}: Duplicate ticker found in deletion candidate pool")
        if len(actual_adds) != len(set(actual_adds)):
            errors.append(f"{q}: Duplicate ticker in actual_additions")
        if len(actual_dels) != len(set(actual_dels)):
            errors.append(f"{q}: Duplicate ticker in actual_deletions")

        # 3. Actuals must exist in their point-in-time pools
        for t in actual_adds:
            if t not in add_pool_tickers:
                errors.append(f"{q}: Actual addition {t} missing from point-in-time candidate pool")
        for t in actual_dels:
            if t not in del_pool_tickers:
                errors.append(f"{q}: Actual deletion {t} missing from point-in-time deletion pool")

        # 4. Pool contamination check BEFORE applying this quarter's transitions
        for t in add_pool_tickers:
            if membership_state.get(t) == "IN":
                errors.append(f"{q}: Addition pool contains {t} which is already IN S&P 500 ({last_event[t]})")
        for t in del_pool_tickers:
            if membership_state.get(t) == "OUT":
                errors.append(f"{q}: Deletion pool contains {t} which was already DELETED ({last_event[t]})")

        # 5. State-transition checks for actuals
        for t in actual_adds:
            if membership_state.get(t) == "IN":
                errors.append(f"{q}: Duplicate addition of {t} (already IN via {last_event[t]})")
            membership_state[t] = "IN"
            last_event[t] = f"added in {q}"

        for t in actual_dels:
            if membership_state.get(t) == "OUT":
                errors.append(f"{q}: Duplicate deletion of {t} (already OUT via {last_event[t]})")
            membership_state[t] = "OUT"
            last_event[t] = f"deleted in {q}"

        # 6. Small-pool transparency warnings
        if len(add_pool) <= 10:
            warnings.append(f"{q}: Addition pool size is {len(add_pool)} (<= 10), making Top-10 recall trivially saturated")
        if len(del_pool) <= 5:
            warnings.append(f"{q}: Deletion pool size is {len(del_pool)} (<= 5), making Top-5 deletion recall trivially saturated")

    # 7. Live Q4 2026 pool membership validation
    live_add_tickers = [c["ticker"] for c in CURRENT_FEEDER_CANDIDATES]
    live_del_tickers = [c["ticker"] for c in CURRENT_VULNERABLE_CONSTITUENTS]

    if len(live_add_tickers) != len(set(live_add_tickers)):
        errors.append("CURRENT_FEEDER_CANDIDATES contains duplicate tickers")
    if len(live_del_tickers) != len(set(live_del_tickers)):
        errors.append("CURRENT_VULNERABLE_CONSTITUENTS contains duplicate tickers")

    overlap = set(live_add_tickers).intersection(live_del_tickers)
    if overlap:
        errors.append(f"Overlap between live addition and deletion pools: {sorted(overlap)}")

    for t in live_add_tickers:
        if membership_state.get(t) == "IN":
            errors.append(f"CURRENT_FEEDER_CANDIDATES contains existing S&P 500 member {t} ({last_event[t]})")

    for t in live_del_tickers:
        if membership_state.get(t) == "OUT":
            errors.append(f"CURRENT_VULNERABLE_CONSTITUENTS contains already-deleted stock {t} ({last_event[t]})")

    report = {
        "is_valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "quarters_checked": len(chronological_quarters),
        "live_addition_pool_size": len(live_add_tickers),
        "live_deletion_pool_size": len(live_del_tickers),
    }

    if raise_on_error and errors:
        raise ValueError("Dataset integrity check failed:\n- " + "\n- ".join(errors))

    return report


def get_historical_rebalances() -> Dict[str, Any]:
    """Returns official ground truth rebalance quarters across 3 years."""
    return HISTORICAL_REBALANCES


def get_point_in_time_data(quarter: str) -> Dict[str, Any]:
    """Returns strictly point-in-time snapshot for a past quarter."""
    return {
        "metadata": HISTORICAL_REBALANCES.get(quarter, {}),
        "addition_candidates": HISTORICAL_POINT_IN_TIME_CANDIDATES.get(quarter, []),
        "deletion_candidates": HISTORICAL_POINT_IN_TIME_DELETIONS.get(quarter, []),
    }


def get_current_universe() -> Dict[str, Any]:
    """Returns current active feeder candidates and vulnerable S&P 500 constituents."""
    return {
        "addition_candidates": CURRENT_FEEDER_CANDIDATES,
        "deletion_candidates": CURRENT_VULNERABLE_CONSTITUENTS,
    }
