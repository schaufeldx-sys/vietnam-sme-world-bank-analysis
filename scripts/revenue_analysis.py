"""
Revenue analysis - comprehensive breakdown.
"""
import sys
sys.path.insert(0, 'src')
from load_microdata import load_firm_level_data, prepare_microdata
import pandas as pd

df = prepare_microdata(load_firm_level_data())

# d2 = total annual sales (VND)
df['revenue'] = pd.to_numeric(df['d2'], errors='coerce')
df['revenue_prev'] = pd.to_numeric(df['d2a1'], errors='coerce')

print("=" * 70)
print("REVENUE ANALYSIS - VIETNAM ENTERPRISE SURVEY 2023")
print("=" * 70)

print(f"\nFirms with revenue data: {df['revenue'].notna().sum():,} of {len(df):,}")
print(f"Coverage: {df['revenue'].notna().mean()*100:.1f}%")

print("\n" + "=" * 70)
print("OVERALL REVENUE STATISTICS (in billion VND)")
print("=" * 70)
valid = df['revenue'].dropna()
print(f"  N: {len(valid)}")
print(f"  Mean: {valid.mean()/1e9:.2f} billion VND")
print(f"  Median: {valid.median()/1e9:.2f} billion VND")
print(f"  Min: {valid.min()/1e9:.4f} billion VND")
print(f"  Max: {valid.max()/1e9:.2f} billion VND")
print(f"  Total: {valid.sum()/1e12:.2f} trillion VND")

# Convert to USD (1 USD ~ 25,000 VND)
print(f"\n  In USD (approx, 25,000 VND/USD):")
print(f"  Mean: {valid.mean()/25e6:.2f} million USD")
print(f"  Median: {valid.median()/25e6:.2f} million USD")
print(f"  Total: {valid.sum()/25e9:.2f} billion USD")

print("\n" + "=" * 70)
print("REVENUE BY FIRM SIZE (billion VND)")
print("=" * 70)
print(f"{'Size':<15} {'N':>5} {'Mean':>12} {'Median':>12}")
for size in ['Small (5-19)', 'Medium (20-99)', 'Large (100+)']:
    sub = df[df['size_label'] == size]
    rev = sub['revenue'].dropna()
    if len(rev) > 0:
        print(f"{size:<15} {len(rev):>5} {rev.mean()/1e9:>12.2f} {rev.median()/1e9:>12.2f}")

print("\n" + "=" * 70)
print("REVENUE BY REGION (billion VND)")
print("=" * 70)
print(f"{'Region':<35} {'N':>5} {'Mean':>12} {'Median':>12}")
for reg in df['region_label'].value_counts().index:
    sub = df[df['region_label'] == reg]
    rev = sub['revenue'].dropna()
    if len(rev) > 0:
        print(f"{reg:<35} {len(rev):>5} {rev.mean()/1e9:>12.2f} {rev.median()/1e9:>12.2f}")

print("\n" + "=" * 70)
print("REVENUE vs BANKING ACCESS")
print("=" * 70)

DK = "Don't know (spontaneous)"

# Has bank account by revenue quartile
df['rev_quartile'] = pd.qcut(df['revenue'], 4, labels=['Q1 (lowest)', 'Q2', 'Q3', 'Q4 (highest)'])

print(f"\n{'Revenue Quartile':<20} {'N':>5} {'Acct%':>8} {'Loan%':>8}")
for q in ['Q1 (lowest)', 'Q2', 'Q3', 'Q4 (highest)']:
    sub = df[df['rev_quartile'] == q]
    n = len(sub)
    if n > 0:
        valid_acc = sub['k4'][sub['k4'] != DK]
        valid_loan = sub['k7'][sub['k7'] != DK]
        acc_pct = (valid_acc == 'Yes').mean() * 100 if len(valid_acc) > 0 else 0
        loan_pct = (valid_loan == 'Yes').mean() * 100 if len(valid_loan) > 0 else 0
        print(f"{q:<20} {n:>5} {acc_pct:>8.1f} {loan_pct:>8.1f}")

print("\n" + "=" * 70)
print("YEAR-OVER-YEAR GROWTH (panel firms)")
print("=" * 70)
# Compare d2 (current) vs d2a1 (3 years ago)
panel = df[['revenue', 'revenue_prev']].dropna()
print(f"Firms with both years: {len(panel)}")
if len(panel) > 0:
    panel['growth'] = (panel['revenue'] - panel['revenue_prev']) / panel['revenue_prev'] * 100
    print(f"Mean 3-year growth: {panel['growth'].mean():.1f}%")
    print(f"Median 3-year growth: {panel['growth'].median():.1f}%")
    print(f"Positive growth: {(panel['growth'] > 0).mean()*100:.1f}%")
    print(f"Declining: {(panel['growth'] < 0).mean()*100:.1f}%")
