"""
Find ownership/state columns.
"""
import sys
sys.path.insert(0, 'src')
from db import query

# Check all b-section columns
b_cols = ['b1', 'b3a', 'b2a', 'b2b', 'b2c', 'b2d', 'b4', 'b4a', 'b5', 'b6', 'b6b', 'b7', 'b7a', 'b8', 'b8x']
for c in b_cols:
    df = query(f'SELECT "{c}", COUNT(*) AS n FROM firms GROUP BY "{c}" ORDER BY n DESC LIMIT 4')
    if len(df) > 0:
        print(f"\n{c}:")
        for _, r in df.iterrows():
            print(f"  {r[c]!r}: {r['n']}")
