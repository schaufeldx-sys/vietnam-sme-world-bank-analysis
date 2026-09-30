"""
Check all financial/revenue variables.
"""
import sys
sys.path.insert(0, 'src')
from load_microdata import load_firm_level_data
import pandas as pd
df = load_firm_level_data()
print("=" * 70)
print("REVENUE & FINANCIAL VARIABLES")
print("=" * 70)

cols_to_check = ['d1', 'd1a3', 'd2', 'd2a1', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9']

for c in cols_to_check:
    if c not in df.columns:
        continue
    numeric = pd.to_numeric(df[c], errors='coerce')
    valid = numeric.dropna()
    print(f"\n{c}:")
    print(f"  N: {len(valid)}")
    if len(valid) > 0 and pd.api.types.is_numeric_dtype(valid):
        print(f"  Min: {valid.min():,.0f}")
        print(f"  Max: {valid.max():,.0f}")
        print(f"  Mean: {valid.mean():,.0f}")
        print(f"  Median: {valid.median():,.0f}")
    elif len(valid) > 0:
        print(f"  Sample values: {valid.head().tolist()}")
