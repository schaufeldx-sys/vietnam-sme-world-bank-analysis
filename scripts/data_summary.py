"""
Comprehensive Vietnam 2023 Microdata Summary.
"""
import sys
sys.path.insert(0, 'src')
from load_microdata import load_firm_level_data, prepare_microdata
import pandas as pd

df = prepare_microdata(load_firm_level_data())
DK = "Don't know (spontaneous)"

# Helper
def pct_yes(series):
    valid = series[series != DK]
    return (valid == 'Yes').mean() * 100 if len(valid) > 0 else 0

print("=" * 75)
print("VIETNAM ENTERPRISE SURVEY 2023 - COMPREHENSIVE DATA SUMMARY")
print("=" * 75)
print(f"\nSample: {len(df):,} firms | 358 variables\n")

# ============= 1. SIZE =============
print("=" * 75)
print("1. FIRM SIZE DISTRIBUTION")
print("=" * 75)
for size in ['Small (5-19)', 'Medium (20-99)', 'Large (100+)']:
    n = (df['size_label'] == size).sum()
    print(f"  {size:25s}: {n:4d} ({n/len(df)*100:.1f}%)")
print(f"  {'TOTAL':25s}: {len(df):4d}")

# ============= 2. INDUSTRY =============
print("\n" + "=" * 75)
print("2. TOP INDUSTRIES (10+ firms)")
print("=" * 75)
industry_dist = df['industry_cat'].value_counts()
for ind, n in industry_dist.items():
    if n >= 10:
        print(f"  {ind:35s}: {n:3d} ({n/len(df)*100:.1f}%)")

# ============= 3. REGION =============
print("\n" + "=" * 75)
print("3. REGIONAL DISTRIBUTION")
print("=" * 75)
for reg, n in df['region_label'].value_counts().items():
    print(f"  {reg:35s}: {n:3d} ({n/len(df)*100:.1f}%)")

# ============= 4. OWNERSHIP =============
print("\n" + "=" * 75)
print("4. OWNERSHIP (% of shares held)")
print("=" * 75)
# b2a = private domestic, b2b = state, b2c = foreign, b2d = other
for var, name in [('b2a', 'Private domestic'), ('b2b', 'State'), ('b2c', 'Foreign'), ('b2d', 'Other')]:
    valid = pd.to_numeric(df[var], errors='coerce')
    valid = valid[valid > 0]
    if len(valid) > 0:
        mean_share = valid.mean()
        median_share = valid.median()
        print(f"  {name:20s}: mean={mean_share:.1f}%, median={median_share:.0f}%, N={len(valid)}")

# ============= 5. BANKING ACCESS =============
print("\n" + "=" * 75)
print("5. BANKING ACCESS (Overall)")
print("=" * 75)
for col, desc in [('k4', 'Has Bank Account'),
                  ('k7', 'Has Bank Loan'),
                  ('k13', 'Loans Require Collateral'),
                  ('k21', 'Loan Application Rejected')]:
    pct = pct_yes(df[col])
    print(f"  {desc:30s}: {pct:.1f}%")

# ============= 6. FINANCE OBSTACLE =============
print("\n" + "=" * 75)
print("6. FINANCE OBSTACLE PERCEPTION")
print("=" * 75)
obstacle_order = ['No obstacle', 'Minor obstacle', 'Moderate obstacle',
                  'Major obstacle', 'Very severe obstacle']
for cat in obstacle_order:
    n = (df['k30'] == cat).sum()
    print(f"  {cat:25s}: {n:3d} ({n/len(df)*100:.1f}%)")
major_severe = df['k30'].isin(['Major obstacle', 'Very severe obstacle']).sum()
print(f"  {'>>> MAJOR + VERY SEVERE':25s}: {major_severe:3d} ({major_severe/len(df)*100:.1f}%)")

# ============= 7. BY SIZE =============
print("\n" + "=" * 75)
print("7. KEY METRICS BY FIRM SIZE")
print("=" * 75)
print(f"{'Size':<15} {'N':>5} {'Acct%':>7} {'Loan%':>7} {'Collat%':>8} {'Reject%':>8} {'Obst%':>7}")
for size in ['Small (5-19)', 'Medium (20-99)', 'Large (100+)']:
    sub = df[df['size_label'] == size]
    n = len(sub)
    if n > 0:
        acc = pct_yes(sub['k4'])
        loan = pct_yes(sub['k7'])
        coll = pct_yes(sub['k13'])
        rej = pct_yes(sub['k21'])
        obst = sub['k30'].isin(['Major obstacle', 'Very severe obstacle']).mean() * 100
        print(f"{size:<15} {n:>5} {acc:>7.1f} {loan:>7.1f} {coll:>8.1f} {rej:>8.1f} {obst:>7.1f}")

# ============= 8. BY REGION =============
print("\n" + "=" * 75)
print("8. KEY METRICS BY REGION")
print("=" * 75)
print(f"{'Region':<35} {'N':>5} {'Acct%':>7} {'Loan%':>7} {'Obst%':>7}")
for reg in df['region_label'].value_counts().index:
    sub = df[df['region_label'] == reg]
    n = len(sub)
    if n > 0:
        acc = pct_yes(sub['k4'])
        loan = pct_yes(sub['k7'])
        obst = sub['k30'].isin(['Major obstacle', 'Very severe obstacle']).mean() * 100
        print(f"{reg:<35} {n:>5} {acc:>7.1f} {loan:>7.1f} {obst:>7.1f}")

# ============= 9. KEY INSIGHTS =============
print("\n" + "=" * 75)
print("KEY INSIGHTS")
print("=" * 75)
small_acc = pct_yes(df[df['size_label']=='Small (5-19)']['k4'])
large_acc = pct_yes(df[df['size_label']=='Large (100+)']['k4'])
print(f"1. Bank account access gap (Large vs Small): {large_acc - small_acc:.1f} pp")
print(f"2. Only {small_acc:.1f}% of small firms have bank accounts")
print(f"3. Only {df['k7'].apply(lambda x: x == 'Yes').mean()*100:.1f}% of all firms have bank loans")
print(f"4. {df['k30'].isin(['Major obstacle','Very severe obstacle']).mean()*100:.1f}% see finance as a major obstacle")
