import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%center%' ORDER BY 1, 2;")
for s, t in cur.fetchall():
    cur.execute(f"SELECT count(*) FROM {s}.{t}")
    print(f"{s}.{t}: {cur.fetchone()[0]}")
cur.close()
conn.close()

