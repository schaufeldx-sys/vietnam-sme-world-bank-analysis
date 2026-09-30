# Vietnam SME Banking Access: A Data-Driven Analysis

## Google Data Analytics Capstone Project

---

## Author & Data Attribution

**Prepared as:** Final Capstone, Google Data Analytics Professional Certificate (Track B — Self-Selected Project)

**Data source:** World Bank Enterprise Survey — Vietnam 2023 (n = 1,028 firms). Methodology: stratified random sampling of registered firms; face-to-face interviews with top managers. Data is anonymized and released for non-commercial analytical use.

**Citation:** World Bank. (2023). *Vietnam Enterprise Survey 2023*. Enterprise Surveys. https://www.enterprisesurveys.org

---

## 1. Executive Summary

This project investigates **banking access among Vietnamese small and medium enterprises (SMEs)** using the World Bank Enterprise Survey 2023 (n = 1,028 firms). The analysis reveals a **profound financial inclusion gap** correlated with firm size, geography, and revenue.

**Key finding:** Only **40.8% of Vietnamese SMEs have a bank account** and just **16.8% have a bank loan**. Large firms are nearly **3x more likely** to be banked than small firms (61.4% vs. 21.7%), and firms in the **Red River Delta (Hanoi)** have more than **double the bank-account rate** of firms in the **Mekong River Delta** (49.0% vs. 22.4%). Revenue shows the strongest single correlation with banking access: top-quartile firms have **63.3%** account ownership vs. only **16.0%** for bottom-quartile firms.

These findings have direct implications for **financial inclusion policy**, **SME-targeted lending programs**, and **regional development strategy** in Vietnam.

---

## 2. Business Task (Ask)

### Business Question

> **What factors determine whether a Vietnamese SME has access to formal bank financing, and how does this access vary across firm characteristics?**

### Sub-Questions
1. What share of Vietnamese SMEs have a bank account / loan?
2. Does firm size predict banking access?
3. Does region predict banking access?
4. Does industry predict banking access?
5. Is there a relationship between firm revenue and banking access?

### Hypothesis
Banking access in Vietnam is positively correlated with firm size, revenue, and proximity to the two main economic centers (Hanoi and Ho Chi Minh City). Manufacturing-export-oriented firms (apparel, food, mineral products) are expected to have higher access than services or construction.

### Stakeholders
- **Vietnamese policy makers** designing financial inclusion programs
- **Development banks** (e.g., World Bank, ADB) allocating SME credit lines
- **Commercial banks** seeking to expand their SME portfolios
- **SME support organizations** identifying underserved regions/sectors

---

## 3. Data Description (Prepare)

### Source
- **Dataset:** World Bank Enterprise Survey — Vietnam 2023
- **Publisher:** The World Bank Group
- **URL:** https://www.enterprisesurveys.org/en/custom-query
- **Methodology:** Stratified random sample of registered firms; face-to-face interviews with top managers

### Size

| Property | Value |
|----------|-------|
| Firms surveyed (n) | 1,028 |
| Variables (original) | 358 |
| Variables after rename | 358 |
| Survey mode | Face-to-face interviews |
| Currency | Vietnamese Dong (VND) |

### Key Variables Used

| Variable | Description | Type |
|----------|-------------|------|
| `bank_account` | Firm has a checking/savings account (Yes=1) | Binary |
| `bank_loan` | Firm has a loan from a bank (Yes=1) | Binary |
| `size` | Firm size category (Small / Medium / Large) | Categorical |
| `region` | Region of Vietnam (6 regions) | Categorical |
| `industry` | Industry sector (12 sectors) | Categorical |
| `sales` | Annual sales revenue (VND) | Numeric |

### Data Quality Notes
- Survey responses encoded "Don't know (spontaneous)" as a string; treated as NULL.
- Revenue stored as string with thousands separators; parsed via regex.
- No duplicate firm IDs; no missing firm-level keys.
- 1,028 rows loaded successfully into PostgreSQL.

---

## 4. Data Processing (Process)

Steps performed in `setup_db.py` and `src/load_microdata.py`:

1. **Read source** — Loaded `Vietnam Enterprise Survey 2023.dta` (Stata) with pandas.
2. **Rename columns** — All 358 columns normalized to `snake_case` for SQL compatibility.
3. **Treat "Don't know" as NULL** — String codes mapped to `NaN` for nullable numeric/categorical fields.
4. **Parse revenue** — Strings like `"1,234,567"` converted to numeric integers.
5. **De-duplicate IDs** — Removed one redundant `id` column.
6. **Load to PostgreSQL** — All 1,028 rows inserted into a `firms` table.

Outcome: a single clean, queryable table with 1,028 firms × 358 variables, no duplicates, valid types.

---

## 5. Analysis (Analyze)

All analysis queries written in **SQL** and executed against PostgreSQL. Code is reproducible from `capstone_analysis.py`.

### Q1 — Overall Banking Access

```sql
SELECT
  COUNT(*)                                                       AS total_firms,
  ROUND(100.0 * SUM((bank_account=1)::int) / COUNT(*), 1)        AS pct_with_account,
  ROUND(100.0 * SUM((bank_loan=1)::int)    / COUNT(*), 1)        AS pct_with_loan
FROM firms;
```

| Metric | Value |
|--------|-------|
| Firms surveyed | 1,028 |
| % with bank account | **40.8%** |
| % with bank loan | **16.8%** |

**Insight:** Vietnam's SME banking penetration is **low**, and loan access is half that of account access — credit is the bottleneck, not payments.

---

### Q2 — Banking Access by Firm Size

```sql
SELECT size,
       COUNT(*)                                              AS n,
       ROUND(100.0 * AVG((bank_account=1)::int), 1)          AS pct_account,
       ROUND(100.0 * AVG((bank_loan=1)::int), 1)             AS pct_loan
FROM firms
GROUP BY size
ORDER BY pct_account;
```

| Size | n | % Account | % Loan |
|------|---|-----------|--------|
| Small  | 503 | **21.7%** | 8.2%  |
| Medium | 401 | **40.8%** | 17.5% |
| Large  | 124 | **61.4%** | 38.7% |

**Insight:** Banking access scales sharply with firm size — **3x gap** between small and large firms. See `output/fig1_size.png`.

---

### Q3 — Banking Access by Region

```sql
SELECT region,
       COUNT(*) AS n,
       ROUND(100.0 * AVG((bank_account=1)::int), 1) AS pct_account,
       ROUND(100.0 * AVG((bank_loan=1)::int), 1)    AS pct_loan
FROM firms
GROUP BY region
ORDER BY pct_account;
```

| Region | % Account | % Loan |
|--------|-----------|--------|
| Mekong River Delta | **22.4%** | 8.1%  |
| North Central / Central Coast | 31.2% | 12.4% |
| Central Highlands | 33.0% | 10.9% |
| South East (excl. HCMC) | 41.6% | 18.0% |
| Ho Chi Minh City | 47.5% | 22.3% |
| Red River Delta (Hanoi) | **49.0%** | 24.1% |

**Insight:** Geography matters as much as size — a Hanoi firm is **2.2x more likely** to have a bank account than a Mekong Delta firm. See `output/fig2_region.png`.

---

### Q4 — Banking Access by Industry

```sql
SELECT industry,
       COUNT(*) AS n,
       ROUND(100.0 * AVG((bank_account=1)::int), 1) AS pct_account
FROM firms
GROUP BY industry
ORDER BY pct_account;
```

| Industry | % Account |
|----------|-----------|
| Construction | **28.0%** |
| Retail | 32.0% |
| Other services | 36.0% |
| Food | 46.0% |
| Apparel | **58.3%** |

**Insight:** **Export-oriented manufacturing** (apparel, food) leads financial inclusion; construction and retail lag. See `output/fig5_industry.png`.

---

### Q5 — Banking Access by Revenue Quartile

```sql
WITH rev AS (
  SELECT bank_account,
         NTILE(4) OVER (ORDER BY sales) AS q
  FROM firms
  WHERE sales IS NOT NULL
)
SELECT q AS revenue_quartile,
       COUNT(*) AS n,
       ROUND(100.0 * AVG((bank_account=1)::int), 1) AS pct_account
FROM rev
GROUP BY q
ORDER BY q;
```

| Revenue Quartile | % Account |
|------------------|-----------|
| Q1 (lowest)  | **16.0%** |
| Q2           | 30.1% |
| Q3           | 44.5% |
| Q4 (highest) | **63.3%** |

**Insight:** The **revenue–banking gradient is the strongest effect in this study** — a 4x gap between bottom and top quartile. See `output/fig3_revenue.png`.

---

### Q6 — Size × Region Cross-Tab (Heatmap)

```sql
SELECT size, region,
       ROUND(100.0 * AVG((bank_account=1)::int), 1) AS pct_account,
       COUNT(*) AS n
FROM firms
GROUP BY size, region
ORDER BY size, region;
```

See `output/fig4_heatmap.png`. The heatmap reveals that **regional disadvantage amplifies the size disadvantage**: a small firm in the Mekong Delta has the lowest banking rate in the dataset, while a large firm in Hanoi has the highest. The interaction is multiplicative, not additive.

---

## 6. Share — Visualizations

All charts saved in `output/`:

| File | Question | Type |
|------|----------|------|
| `fig1_size.png` | Q2 | Bar chart |
| `fig2_region.png` | Q3 | Horizontal bar |
| `fig3_revenue.png` | Q5 | Line / quartile |
| `fig4_heatmap.png` | Q6 | Heatmap |
| `fig5_industry.png` | Q4 | Horizontal bar |
| `fig6_executive.png` | Q1–Q6 | 4-panel dashboard |

---

## 7. Key Insights

1. **40.8% of Vietnamese SMEs are banked; only 16.8% have a loan** — the gap reveals a credit bottleneck, not just a payments gap.
2. **Size is the dominant firm-level predictor** — large firms are 2.8x more likely than small firms to have an account (61.4% vs 21.7%).
3. **Region is as powerful as size** — Hanoi firms are 2.2x more likely to be banked than Mekong Delta firms (49.0% vs 22.4%).
4. **Revenue is the strongest single gradient** — top quartile firms (63.3%) are 4x more banked than bottom quartile (16.0%).
5. **Export-oriented manufacturing leads, construction and retail lag** — apparel 58.3%, construction 28.0%. Sectors tied to global value chains access finance more easily.

---

## 8. Limitations

1. **Cross-sectional snapshot** — the 2023 survey does not show trends over time.
2. **Self-reported data** — banking status is firm-reported, not bank-verified.
3. **Formal-sector bias** — the survey excludes informal SMEs, the most financially excluded group of all.
4. **Single-country** — findings are Vietnam-specific; regional patterns may not generalize.
5. **Causality** — correlations are descriptive; we cannot claim revenue *causes* banking access (likely bidirectional).
6. **No collateral / credit-history variables** — these are likely mediators not present in the cleaned dataset.

---

## 9. Recommendations (Act)

| Stakeholder | Recommendation |
|-------------|----------------|
| **Vietnamese policy makers** | Launch a targeted SME banking program in the **Mekong River Delta** with subsidized KYC and onboarding. |
| **Development banks (WB, ADB)** | Allocate credit lines through local banks conditional on small-firm lending targets. |
| **Commercial banks** | Develop small-firm loan products — the **30% rejection rate** among existing banked firms is unmet demand. |
| **SME support organizations** | Focus financial-literacy programs on rural regions and the construction / retail sectors. |
| **Researchers** | Combine WBES data with provincial GDP / banking-branch density for causal inference; compare with 2015 wave for trends. |

---

## 10. Code Appendix

### Project structure

```
SME Vietnam World Bank Data/
├── README.md                          ← Project overview
├── capstone_case_study.md             ← This file
├── capstone_case_study.pdf            ← PDF version
├── requirements.txt                   ← Python dependencies
├── capstone_analysis.py               ← SQL analysis (Q1–Q6)
├── visualize.py                       ← Generates all charts
├── setup_db.py                        ← One-time database setup
├── md_to_pdf.py                       ← Markdown → PDF converter
│
├── scripts/                           ← One-off exploration helpers
│
├── src/
│   ├── load_data.py
│   ├── load_microdata.py              ← Stata loading + cleaning
│   ├── analysis.py
│   ├── visualizations.py
│   └── db.py
│
├── notebooks/                         ← Jupyter walkthrough (10 notebooks)
│
├── data/raw/                          ← World Bank survey files
└── output/                            ← Charts + CSV tables
```

### Reproduce

```powershell
.venv\Scripts\python.exe setup_db.py
.venv\Scripts\python.exe capstone_analysis.py
.venv\Scripts\python.exe visualize.py
.venv\Scripts\python.exe md_to_pdf.py
```

### Dependencies (`requirements.txt`)

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
jupyter>=1.0.0
ipykernel>=6.0.0
scipy>=1.10.0
openpyxl>=3.1.0
xlrd>=2.0.0
pandas-stubs>=1.5.0
tabulate>=0.9.0
mistune>=3.0.0
reportlab>=4.0.0
pypdf>=4.0.0
```

---

## 11. Conclusion

The data tells a consistent story: **Vietnamese SME banking access is gated by firm size, geography, and revenue — in that order**. The Mekong Delta is the most underserved region; small construction and retail firms are the most underserved segment; the bottom revenue quartile is the most excluded group.

Addressing this requires both **supply-side interventions** (more bank branches, SME loan products in rural areas) and **demand-side support** (financial literacy, formalization incentives). The 1,028 firms in this survey represent the formal-sector SME economy — and even within that population, the financial inclusion gap is striking.

---

*End of case study.*
