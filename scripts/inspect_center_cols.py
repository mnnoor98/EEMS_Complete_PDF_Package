import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'polling' AND table_name = 'centers';")
print("polling.centers:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'polling' AND table_name = 'booths';")
print("polling.booths:", [r[0] for r in cur.fetchall()])
cur.close()
conn.close()

