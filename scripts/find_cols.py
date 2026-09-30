"""
Find right column names for industry and ownership.
"""
import sys
sys.path.insert(0, 'src')
from db import query

# Find columns that might be industry/ownership
sql = """
SELECT column_name FROM information_schema.columns
WHERE table_name = 'firms'
ORDER BY ordinal_position
"""
cols = query(sql)
print("All columns:")
for c in cols['column_name']:
    if 'industry' in c.lower() or 'sector' in c.lower() or 'owner' in c.lower():
        print("  >>>", c)
