"""
Database setup and data loading for Vietnam Enterprise Survey.
"""
import psycopg2
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'src')
from load_microdata import load_firm_level_data, prepare_microdata

# Connection config
DB_CONFIG = {
    'host': 'localhost',
    'port': 2312,
    'user': 'postgres',
    'password': '23122001Hh',
    'database': 'postgres'
}
DB_NAME = 'vietnam_sme'

def connect(dbname='postgres'):
    cfg = DB_CONFIG.copy()
    cfg['database'] = dbname
    return psycopg2.connect(**cfg)

def create_database():
    """Create the vietnam_sme database if it doesn't exist."""
    conn = connect('postgres')
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE {DB_NAME}')
        print(f"Created database: {DB_NAME}")
    else:
        print(f"Database {DB_NAME} already exists")
    cur.close()
    conn.close()

def load_firms_to_db():
    """Load firm-level survey data into PostgreSQL."""
    print("Loading firm-level data...")
    df = prepare_microdata(load_firm_level_data())

    # Drop existing id column (we'll use a serial PK)
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # Clean column names for SQL
    df.columns = [str(c).lower().replace('/', '_').replace('-', '_').replace(' ', '_')[:63]
                  for c in df.columns]

    print(f"  Shape: {df.shape}")

    conn = connect(DB_NAME)
    cur = conn.cursor()

    # Drop and recreate table
    cur.execute('DROP TABLE IF EXISTS firms CASCADE')
    col_defs = [f'"{c}" TEXT' for c in df.columns]
    create_sql = 'CREATE TABLE firms (id BIGSERIAL PRIMARY KEY, ' + ','.join(col_defs) + ')'
    cur.execute(create_sql)

    # Insert data
    print(f"  Inserting {len(df)} rows...")
    cols = list(df.columns)
    placeholders = ','.join(['%s'] * (len(cols) + 1))
    quoted_cols = ['"' + c + '"' for c in cols]
    col_list = ','.join(quoted_cols)
    insert_sql = 'INSERT INTO firms (id, ' + col_list + ') VALUES (' + placeholders + ')'

    for idx, row in df.iterrows():
        vals = [idx] + [None if pd.isna(v) else str(v) for v in row.values]
        cur.execute(insert_sql, vals)

    conn.commit()
    cur.execute('SELECT COUNT(*) FROM firms')
    print(f"  Inserted {cur.fetchone()[0]} firms")
    cur.close()
    conn.close()
    return df

def main():
    create_database()
    load_firms_to_db()
    print("\n✓ Database setup complete!")

if __name__ == '__main__':
    main()
