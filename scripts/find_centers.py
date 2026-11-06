import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%center%' ORDER BY 1;")
for t in cur.fetchall():
    print("Table:", t[0])
    cur.execute(f"SELECT count(*) FROM polling.{t[0]}" if 'polling' in t[0] else f"SELECT count(*) FROM {t[0]}")
    print("Count:", cur.fetchone()[0])
cur.close()
conn.close()

