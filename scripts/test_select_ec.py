import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT * FROM polling.election_centers;")
rows = cur.fetchall()
print("Direct select count:", len(rows))
for r in rows:
    print(r)
cur.close()
conn.close()

