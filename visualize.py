"""
Generate visualizations for the Google Data Analytics Capstone project.
"""
import sys
sys.path.insert(0, 'src')
from db import query
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Color palette
COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B9C70', '#6A4C93']

# =============================================================================
# FIGURE 1: Banking Access by Firm Size (Grouped Bar)
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
df = query('''
    SELECT size_label,
           ROUND(100.0 * SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_account,
           ROUND(100.0 * SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loan
    FROM firms
    WHERE size_label IS NOT NULL
    GROUP BY size_label
    ORDER BY CASE size_label WHEN 'Small (5-19)' THEN 1 WHEN 'Medium (20-99)' THEN 2 WHEN 'Large (100+)' THEN 3 END
''')

x = np.arange(len(df))
width = 0.35
bars1 = ax.bar(x - width/2, df['pct_account'], width, label='Has Bank Account', color=COLORS[0])
bars2 = ax.bar(x + width/2, df['pct_loan'], width, label='Has Bank Loan', color=COLORS[1])

ax.bar_label(bars1, fmt='%.1f%%', padding=3)
ax.bar_label(bars2, fmt='%.1f%%', padding=3)
ax.set_xticks(x)
ax.set_xticklabels(df['size_label'])
ax.set_ylabel('Percentage of Firms (%)')
ax.set_title('Banking Access by Firm Size\nVietnam SMEs 2023', fontsize=14, fontweight='bold')
ax.legend()
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, 75)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig1_size.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved: fig1_size.png")

# =============================================================================
# FIGURE 2: Banking Access by Region (Horizontal Bar)
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
df = query('''
    SELECT region_label,
           ROUND(100.0 * SUM(CASE WHEN k4 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_account,
           ROUND(100.0 * SUM(CASE WHEN k7 = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loan
    FROM firms
    WHERE region_label IS NOT NULL
    GROUP BY region_label
    ORDER BY pct_account
''')

y = np.arange(len(df))
ax.barh(y - 0.2, df['pct_account'], 0.4, label='Has Bank Account', color=COLORS[0])
ax.barh(y + 0.2, df['pct_loan'], 0.4, label='Has Bank Loan', color=COLORS[1])

for i, (acc, ln) in enumerate(zip(df['pct_account'], df['pct_loan'])):
    ax.text(acc + 1, i - 0.2, f'{acc}%', va='center', fontsize=9)
    ax.text(ln + 1, i + 0.2, f'{ln}%', va='center', fontsize=9)

ax.set_yticks(y)
ax.set_yticklabels(df['region_label'])
ax.set_xlabel('Percentage of Firms (%)')
ax.set_title('Banking Access by Region\nVietnam SMEs 2023', fontsize=14, fontweight='bold')
ax.legend()
ax.set_xlim(0, 60)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig2_region.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved: fig2_region.png")

# =============================================================================
# FIGURE 3: Revenue vs Banking Access (Quartiles)
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
df = query('''
    WITH cleaned AS (
        SELECT *,
            CASE WHEN d2 ~ '^[0-9]' THEN CAST(REGEXP_REPLACE(d2, ',', '', 'g') AS NUMERIC)
                 ELSE NULL END AS revenue_num
        FROM firms
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

x = np.arange(len(df))
width = 0.35
bars1 = ax.bar(x - width/2, df['pct_account'], width, label='Has Bank Account', color=COLORS[2])
bars2 = ax.bar(x + width/2, df['pct_loan'], width, label='Has Bank Loan', color=COLORS[3])

ax.bar_label(bars1, fmt='%.1f%%', padding=3)
ax.bar_label(bars2, fmt='%.1f%%', padding=3)
ax.set_xticks(x)
ax.set_xticklabels([f'Q{int(q)}\n({r}B VND)' for q, r in zip(df['revenue_quartile'], df['mean_revenue_bil_vnd'])])
ax.set_ylabel('Percentage of Firms (%)')
ax.set_title('Banking Access by Revenue Quartile\nVietnam SMEs 2023', fontsize=14, fontweight='bold')
ax.legend()
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, 80)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig3_revenue.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved: fig3_revenue.png")

# =============================================================================
# FIGURE 4: Size × Region Heatmap
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
df = pd.read_csv(OUTPUT_DIR / 'q6_size_region.csv')

matrix = df[['small_pct', 'medium_pct', 'large_pct']].values
im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=80)

ax.set_xticks(np.arange(3))
ax.set_xticklabels(['Small (5-19)', 'Medium (20-99)', 'Large (100+)'])
ax.set_yticks(np.arange(len(df)))
ax.set_yticklabels(df['region_label'])

for i in range(len(df)):
    for j in range(3):
        text = ax.text(j, i, f'{matrix[i, j]:.1f}%', ha="center", va="center",
                       color="black" if matrix[i, j] > 40 else "white", fontweight='bold')

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('% with Bank Account', rotation=270, labelpad=20)
ax.set_title('Bank Account Ownership by Size × Region\nVietnam SMEs 2023',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig4_heatmap.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved: fig4_heatmap.png")

# =============================================================================
# FIGURE 5: Banking Access by Industry (top 10)
# =============================================================================
fig, ax = plt.subplots(figsize=(11, 6))
df = pd.read_csv(OUTPUT_DIR / 'q4_by_industry.csv')
df = df.sort_values('pct_account')

y = np.arange(len(df))
ax.barh(y, df['pct_account'], color=COLORS[4])
for i, (val, n) in enumerate(zip(df['pct_account'], df['n_firms'])):
    ax.text(val + 1, i, f'{val}% (n={n})', va='center', fontsize=9)

ax.set_yticks(y)
ax.set_yticklabels(df['industry_cat'])
ax.set_xlabel('% of Firms with Bank Account')
ax.set_title('Banking Access by Industry (Top 10 by Firm Count)\nVietnam SMEs 2023',
             fontsize=14, fontweight='bold')
ax.set_xlim(0, 70)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig5_industry.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved: fig5_industry.png")

# =============================================================================
# FIGURE 6: Executive Summary Dashboard (4 panels)
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Vietnam SME Banking Access — Executive Summary',
             fontsize=16, fontweight='bold')

# Panel 1: Has Account / Loan (Donut-like bars)
ax = axes[0, 0]
total = 1028
with_account = 419
with_loan = 173
ax.pie([with_account, total - with_account], labels=[f'Has Account\n({with_account})', f'No Account\n({total - with_account})'],
       autopct='%1.1f%%', colors=[COLORS[0], '#E0E0E0'], startangle=90,
       wedgeprops=dict(width=0.4))
ax.set_title('Bank Account Access', fontweight='bold')

# Panel 2: Has Loan
ax = axes[0, 1]
ax.pie([with_loan, total - with_loan], labels=[f'Has Loan\n({with_loan})', f'No Loan\n({total - with_loan})'],
       autopct='%1.1f%%', colors=[COLORS[1], '#E0E0E0'], startangle=90,
       wedgeprops=dict(width=0.4))
ax.set_title('Bank Loan Access', fontweight='bold')

# Panel 3: Account by size
ax = axes[1, 0]
df = pd.read_csv(OUTPUT_DIR / 'q2_by_size.csv')
bars = ax.bar(df['size_label'], df['pct_account'], color=COLORS[2])
ax.bar_label(bars, fmt='%.1f%%')
ax.set_title('Account Access by Size', fontweight='bold')
ax.set_ylabel('%')
ax.set_ylim(0, 75)
ax.grid(axis='y', alpha=0.3)

# Panel 4: Account by region
ax = axes[1, 1]
df = pd.read_csv(OUTPUT_DIR / 'q3_by_region.csv')
df = df.sort_values('pct_account')
bars = ax.barh(df['region_label'], df['pct_account'], color=COLORS[4])
ax.bar_label(bars, fmt='%.1f%%', padding=3)
ax.set_title('Account Access by Region', fontweight='bold')
ax.set_xlabel('%')
ax.set_xlim(0, 60)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig6_executive.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved: fig6_executive.png")

print("\nAll 6 figures saved to output/")
