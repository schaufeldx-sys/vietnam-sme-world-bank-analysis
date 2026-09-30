"""
Check industry_cat and look for ownership.
"""
import sys
sys.path.insert(0, 'src')
from db import query

# Check industry_cat
print("industry_cat:")
df = query("SELECT industry_cat, COUNT(*) AS n FROM firms GROUP BY industry_cat ORDER BY n DESC LIMIT 15")
for _, r in df.iterrows():
    print(f"  {r['industry_cat']!r}: {r['n']}")

# Check b section (ownership) - look for columns starting with b
print("\nColumns starting with b:")
all_cols = query("SELECT column_name FROM information_schema.columns WHERE table_name='firms'")
b_cols = [c for c in all_cols['column_name'] if c.startswith('b')][:30]
print(b_cols)

# Look at b5, b6 (ownership)
for c in ['b5', 'b6', 'b1', 'b2']:
    try:
        df = query(f'SELECT "{c}", COUNT(*) AS n FROM firms GROUP BY "{c}" ORDER BY n DESC LIMIT 6')
        if len(df) > 0:
            print(f"\n{c}:")
            for _, r in df.iterrows():
                print(f"  {r[c]!r}: {r['n']}")
    except Exception as e:
        print(f"{c}: {e}")
