"""
=================================================================================
GOOGLE DATA ANALYTICS CAPSTONE PROJECT
=================================================================================
Vietnam SME Banking Access Analysis
World Bank Enterprise Survey 2023
=================================================================================

This script performs the complete analysis for the capstone case study,
following the Ask → Prepare → Process → Analyze → Share methodology.
"""

import sys
sys.path.insert(0, 'src')
from db import query
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path

# Output directory for visualizations
OUTPUT_DIR = Path(__file__).parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10

print("=" * 80)
print("VIETNAM SME BANKING ACCESS ANALYSIS")
print("Google Data Analytics Capstone Project")
print("=" * 80)

# =============================================================================
# ASK: Define business questions
# =============================================================================
"""
BUSINESS TASK:
Identify which factors determine whether a Vietnamese SME has access to
bank financing, and quantify how this access varies across firm characteristics
(size, region, industry, ownership).

KEY QUESTIONS:
Q1: What % of Vietnamese SMEs have bank accounts and loans?
Q2: How does banking access vary by firm size?
Q3: How does banking access vary by region?
Q4: How does banking access vary by industry?
Q5: What is the relationship between revenue and banking access?
"""

# =============================================================================
# PREPARE: Connect to PostgreSQL
# =============================================================================
print("\n[PREPARE] Connecting to PostgreSQL database...")
firm_count = query('SELECT COUNT(*) AS n FROM firms')['n'][0]
print(f"  Loaded {firm_count} firms from PostgreSQL")

# =============================================================================
# PROCESS: Clean data, handle "Don't know" responses
# =============================================================================
print("\n[PROCESS] Cleaning data...")
print("  - Treating 'Don't know (spontaneous)' as NULL")
print("  - Converting revenue fields to numeric")
print("  - Filtering to firms with valid size/region")

# =============================================================================
# ANALYZE: Answer each business question
# =============================================================================

# -------- Q1: Overall banking access --------
print("\n" + "=" * 80)
print("[ANALYZE] Q1: OVERALL BANKING ACCESS")
print("=" * 80)

q1 = query('''
    WITH clean AS (
        SELECT *,
            CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END AS has_account,
            CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END AS has_loan,
            CASE WHEN d2 ~ '^[0-9]' THEN CAST(REGEXP_REPLACE(d2, ',', '', 'g') AS NUMERIC)
                 ELSE NULL END AS revenue,
            CASE WHEN d2a1 ~ '^[0-9]' THEN CAST(REGEXP_REPLACE(d2a1, ',', '', 'g') AS NUMERIC)
                 ELSE NULL END AS revenue_prev
        FROM firms
        WHERE size_label IS NOT NULL
    )
    SELECT
        COUNT(*) AS total_firms,
        SUM(has_account) AS firms_with_account,
        SUM(has_loan) AS firms_with_loan,
        ROUND(100.0 * AVG(has_account), 1) AS pct_account,
        ROUND(100.0 * AVG(has_loan), 1) AS pct_loan,
        ROUND(AVG(revenue)/1e9, 2) AS mean_revenue_bil_vnd,
        ROUND(AVG(revenue)/1e6 / 25, 2) AS mean_revenue_mil_usd
    FROM clean
''')
print(q1.to_string(index=False))

# -------- Q2: Banking access by firm size --------
print("\n" + "=" * 80)
print("[ANALYZE] Q2: BANKING ACCESS BY FIRM SIZE")
print("=" * 80)

q2 = query('''
    SELECT
        size_label,
        COUNT(*) AS n_firms,
        SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) AS with_account,
        SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) AS with_loan,
        ROUND(100.0 * SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_account,
        ROUND(100.0 * SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loan
    FROM firms
    WHERE size_label IS NOT NULL
    GROUP BY size_label
    ORDER BY
        CASE size_label WHEN 'Small (5-19)' THEN 1
                        WHEN 'Medium (20-99)' THEN 2
                        WHEN 'Large (100+)' THEN 3 END
''')
print(q2.to_string(index=False))

# -------- Q3: Banking access by region --------
print("\n" + "=" * 80)
print("[ANALYZE] Q3: BANKING ACCESS BY REGION")
print("=" * 80)

q3 = query('''
    SELECT
        region_label,
        COUNT(*) AS n_firms,
        ROUND(100.0 * SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_account,
        ROUND(100.0 * SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loan
    FROM firms
    WHERE region_label IS NOT NULL
    GROUP BY region_label
    ORDER BY pct_account DESC
''')
print(q3.to_string(index=False))

# -------- Q4: Banking access by industry --------
print("\n" + "=" * 80)
print("[ANALYZE] Q4: BANKING ACCESS BY INDUSTRY (top 10)")
print("=" * 80)

q4 = query('''
    SELECT
        industry_cat,
        COUNT(*) AS n_firms,
        ROUND(100.0 * SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_account,
        ROUND(100.0 * SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loan
    FROM firms
    WHERE industry_cat IS NOT NULL
    GROUP BY industry_cat
    HAVING COUNT(*) >= 20
    ORDER BY pct_account DESC
    LIMIT 10
''')
print(q4.to_string(index=False))

# -------- Q5: Revenue vs banking access --------
print("\n" + "=" * 80)
print("[ANALYZE] Q5: REVENUE vs BANKING ACCESS")
print("=" * 80)

# Compute revenue quartiles
q5 = query('''
    WITH cleaned AS (
        SELECT *,
            CASE WHEN d2 ~ '^[0-9]' THEN CAST(REGEXP_REPLACE(d2, ',', '', 'g') AS NUMERIC)
                 ELSE NULL END AS revenue_num
        FROM firms
        WHERE size_label IS NOT NULL
    ),
    quartiled AS (
        SELECT *,
            NTILE(4) OVER (ORDER BY revenue_num) AS revenue_quartile
        FROM cleaned
        WHERE revenue_num IS NOT NULL
    )
    SELECT
        revenue_quartile,
        COUNT(*) AS n_firms,
        ROUND(AVG(revenue_num)/1e9, 2) AS mean_revenue_bil_vnd,
        ROUND(100.0 * SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_account,
        ROUND(100.0 * SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loan
    FROM quartiled
    GROUP BY revenue_quartile
    ORDER BY revenue_quartile
''')
print(q5.to_string(index=False))

# -------- Q6: Cross-tab size × region --------
print("\n" + "=" * 80)
print("[ANALYZE] Q6: SIZE × REGION CROSS-TAB (% with bank account)")
print("=" * 80)

q6 = query('''
    SELECT
        region_label,
        ROUND(100.0 * SUM(CASE WHEN size_label = 'Small (5-19)' AND k4 = 'Yes' THEN 1 ELSE 0 END) /
              NULLIF(SUM(CASE WHEN size_label = 'Small (5-19)' THEN 1 ELSE 0 END), 0), 1) AS small_pct,
        ROUND(100.0 * SUM(CASE WHEN size_label = 'Medium (20-99)' AND k4 = 'Yes' THEN 1 ELSE 0 END) /
              NULLIF(SUM(CASE WHEN size_label = 'Medium (20-99)' THEN 1 ELSE 0 END), 0), 1) AS medium_pct,
        ROUND(100.0 * SUM(CASE WHEN size_label = 'Large (100+)' AND k4 = 'Yes' THEN 1 ELSE 0 END) /
              NULLIF(SUM(CASE WHEN size_label = 'Large (100+)' THEN 1 ELSE 0 END), 0), 1) AS large_pct
    FROM firms
    WHERE region_label IS NOT NULL AND size_label IS NOT NULL
    GROUP BY region_label
    ORDER BY large_pct DESC
''')
print(q6.to_string(index=False))

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE - data ready for visualizations")
print("=" * 80)

# Save to CSV for later use
q2.to_csv(OUTPUT_DIR / 'q2_by_size.csv', index=False)
q3.to_csv(OUTPUT_DIR / 'q3_by_region.csv', index=False)
q4.to_csv(OUTPUT_DIR / 'q4_by_industry.csv', index=False)
q5.to_csv(OUTPUT_DIR / 'q5_by_revenue.csv', index=False)
q6.to_csv(OUTPUT_DIR / 'q6_size_region.csv', index=False)
print(f"CSV files saved to {OUTPUT_DIR}/")
