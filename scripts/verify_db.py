import psycopg2
conn = psycopg2.connect(host='localhost', port=2312, user='postgres', password='23122001Hh', database='vietnam_sme')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM firms')
print('Firms in DB:', cur.fetchone()[0])
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='firms' ORDER BY ordinal_position LIMIT 15")
print('First 15 columns:')
for r in cur.fetchall():
    print('  ', r[0])
cur.close()
conn.close()
