import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('campaign', 'polling', 'election') ORDER BY 1, 2;")
for r in cur.fetchall():
    print(r)
cur.close()
conn.close()

