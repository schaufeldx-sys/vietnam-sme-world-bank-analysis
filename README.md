# Vietnam SME Banking Access — Google Data Analytics Capstone

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: World Bank](https://img.shields.io/badge/Data-World%20Bank%20Enterprise%20Survey-blue.svg)](https://www.enterprisesurveys.org)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org)

A complete data analytics case study investigating **banking access among Vietnamese small and medium enterprises (SMEs)**, based on the **World Bank Enterprise Survey 2023** (n = 1,028 firms).

This project follows Google's data analysis framework: **Ask → Prepare → Process → Analyze → Share → Act**.

> 📄 **Quick links:** [Case study (Markdown)](capstone_case_study.md) · [Case study (PDF)](capstone_case_study.pdf) · [Output charts](output/)

---

## About the Author

This capstone project was prepared as the final deliverable for the **Google Data Analytics Professional Certificate** (Track B — Self-Selected Project). It demonstrates end-to-end ownership: question framing, data acquisition, cleaning, SQL-based analysis, visualization, and stakeholder recommendations.

---

## About the Data

The data used in this analysis comes from the **World Bank Enterprise Survey (WBES) — Vietnam 2023**, publicly available at https://www.enterprisesurveys.org/en/custom-query. The survey uses stratified random sampling of registered firms and face-to-face interviews with top managers. All data is anonymized and released for non-commercial analytical use.

> **Citation:** World Bank. (2023). *Vietnam Enterprise Survey 2023*. Enterprise Surveys. https://www.enterprisesurveys.org

---

## 🎯 Business Question

> What factors determine whether a Vietnamese SME has access to formal bank financing, and how does this access vary across firm characteristics (size, region, industry, revenue)?

---

## 📊 Key Findings

| Finding | Evidence |
|---------|----------|
| **40.8% of Vietnamese SMEs have a bank account; only 16.8% have a bank loan** | Q1 — overall |
| **Large firms are 2.8x more likely to be banked than small firms** (61.4% vs 21.7%) | Q2 — by size |
| **Mekong Delta is dramatically underserved** — only 22.4% have accounts vs 49.0% in Hanoi | Q3 — by region |
| **Revenue is the strongest predictor** — top-quartile firms 4x more likely to be banked than bottom-quartile | Q5 — by revenue |
| **Export-oriented manufacturing leads** financial inclusion (Apparel 58.3%, Food 46.0%) | Q4 — by industry |
| **Loan access is the real bottleneck** — even banked firms struggle to get credit | Q1 vs Q2 |

---

## 📁 Project Structure

```
SME Vietnam World Bank Data/
├── README.md                          ← This file
├── capstone_case_study.md             ← Full case study report (Markdown)
├── capstone_case_study.pdf            ← PDF version of the case study
├── requirements.txt                   ← Python dependencies
├── .gitignore                         ← Files excluded from version control
│
├── capstone_analysis.py               ← SQL analysis (Q1–Q6)
├── visualize.py                       ← Generates all charts
├── setup_db.py                        ← One-time database setup
├── md_to_pdf.py                       ← Markdown → PDF converter
│
├── scripts/                           ← One-off exploration helpers
│   ├── check_b.py
│   ├── check_industry.py
│   ├── check_ownership.py
│   ├── check_revenue.py
│   ├── data_summary.py
│   ├── explore_columns.py
│   ├── find_cols.py
│   ├── revenue_analysis.py
│   ├── verify_db.py
│   └── verify_deps.py
│
├── src/                               ← Source modules
│   ├── load_data.py                   ← Excel file loading
│   ├── load_microdata.py              ← Stata + cleaning
│   ├── analysis.py
│   ├── visualizations.py
│   └── db.py                          ← PostgreSQL connection
│
├── notebooks/                         ← Jupyter notebooks (analysis walkthrough)
│   ├── 01_data_inspection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   ├── 04_visualizations.ipynb
│   ├── 05_financial_constraints_analysis.ipynb
│   ├── 06_gender_analysis.ipynb
│   ├── 07_regional_comparison.ipynb
│   ├── 08_firm_size_analysis.ipynb
│   ├── 09_conclusions_recommendations.ipynb
│   └── 10_microdata_analysis.ipynb
│
└── output/                            ← Generated charts + tables
    ├── fig1_size.png                  ← Banking by size
    ├── fig2_region.png                ← Banking by region
    ├── fig3_revenue.png               ← Banking by revenue quartile
    ├── fig4_heatmap.png               ← Size × region heatmap
    ├── fig5_industry.png              ← Banking by industry
    ├── fig6_executive.png             ← Executive dashboard
    └── q*.csv                         ← Analysis data tables
```

> ⚠️ **Note:** `data/raw/` is excluded from the repo per the World Bank's terms — re-download it from https://www.enterprisesurveys.org/en/custom-query if you want to reproduce the analysis.

---

## 🛠️ Tech Stack

- **Python 3.14** — pandas, matplotlib, reportlab
- **PostgreSQL 18.4** — primary data store, query engine
- **psycopg2-binary** — Python ↔ PostgreSQL connector
- **Stata .dta** — source survey format
- **mistune + reportlab** — Markdown → PDF rendering

---

## 🚀 Quick Start

### 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Download the data (one time)

Visit https://www.enterprisesurveys.org/en/custom-query, select **Vietnam 2023**, and download the Stata `.dta` file. Save it to `data/raw/Vietnam Enterprise Survey 2023.dta`.

### 3. Set up database (one time)

```powershell
.venv\Scripts\python.exe setup_db.py
```

This creates the `vietnam_sme` database in PostgreSQL and loads all 1,028 firms into a `firms` table.

### 4. Run the analysis

```powershell
.venv\Scripts\python.exe capstone_analysis.py
```

### 5. Generate visualizations

```powershell
.venv\Scripts\python.exe visualize.py
```

### 6. Regenerate the PDF case study

```powershell
.venv\Scripts\python.exe md_to_pdf.py
```

---

## 📖 Analysis Questions

| Q | Question | Output |
|---|----------|--------|
| Q1 | Overall banking access | `40.8% have account, 16.8% have loan` |
| Q2 | Banking by firm size | `21.7% (S) → 40.8% (M) → 61.4% (L)` |
| Q3 | Banking by region | `Mekong 22.4% to Hanoi 49.0%` |
| Q4 | Banking by industry | `Construction 28% to Apparel 58%` |
| Q5 | Banking by revenue | `16% (Q1) → 63% (Q4)` |
| Q6 | Size × region cross-tab | Heatmap reveals geography matters as much as size |

---

## 📚 Documentation

- **[capstone_case_study.md](capstone_case_study.md)** — Full Google-format case study (Markdown)
- **[capstone_case_study.pdf](capstone_case_study.pdf)** — Print-ready PDF version
- **[notebooks/](notebooks/)** — Step-by-step Jupyter walkthrough

---

## 🤝 Contributing

This is a portfolio/academic capstone project, but feedback and suggestions are welcome. Feel free to open an issue or pull request.

---

## 📜 License

- **Data:** World Bank Enterprise Survey — public use, free for non-commercial analysis.
- **Code & analysis:** [MIT License](LICENSE).
