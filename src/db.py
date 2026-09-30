"""
Database query utilities for Vietnam SME data.
"""
import psycopg2
import pandas as pd
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'localhost',
    'port': 2312,
    'user': 'postgres',
    'password': '23122001Hh',
    'database': 'vietnam_sme'
}

@contextmanager
def get_cursor():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def query(sql: str, params=None) -> pd.DataFrame:
    with get_cursor() as cur:
        cur.execute(sql, params)
        if cur.description:
            cols = [d[0] for d in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)
        return pd.DataFrame()

if __name__ == '__main__':
    # Test query
    result = query('SELECT COUNT(*) AS n FROM firms')
    print(f"Total firms: {result['n'][0]}")

    # Banking access by size
    result = query('''
        SELECT size_label,
               COUNT(*) as n,
               COUNT(*) FILTER (WHERE k4 = 'Yes') as has_account
        FROM firms
        WHERE size_label IS NOT NULL
        GROUP BY size_label
        ORDER BY size_label
    ''')
    print(result)
