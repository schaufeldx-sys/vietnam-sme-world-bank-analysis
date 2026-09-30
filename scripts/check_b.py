"""
Check all b variables to find ownership.
"""
import sys
sys.path.insert(0, 'src')
from load_microdata import load_firm_level_data
df = load_firm_level_data()
b_cols = sorted([c for c in df.columns if c.startswith('b')])
for c in b_cols:
    if df[c].dtype.name == 'category':
        cats = df[c].cat.categories.tolist()
        print(f'{c}: {cats[:5]}')
    else:
        print(f'{c}: {df[c].dtype}')
