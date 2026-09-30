"""
Explore finance-related columns for case study.
"""
import sys
sys.path.insert(0, 'src')
from db import query

# Check key finance columns
key_cols = ['k4', 'k7', 'k8', 'k16a', 'k16b', 'k16c', 'k16d', 'k16e', 'k16f', 'k16g', 'k16h', 'k16i',
            'size_label', 'region_label', 'industry_label', 'ownership_label']

print("Column presence and sample values:")
for c in key_cols:
    sql = f"SELECT \"{c}\", COUNT(*) AS n FROM firms GROUP BY \"{c}\" ORDER BY n DESC LIMIT 6"
    try:
        df = query(sql)
        print(f"\n{c}:")
        for _, row in df.iterrows():
            val = row[c] if row[c] else 'NULL'
            print(f"  {val!r}: {row['n']}")
    except Exception as e:
        print(f"{c}: ERROR {e}")
