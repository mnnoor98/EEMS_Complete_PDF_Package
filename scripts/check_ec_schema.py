import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%election_center%';")
print(cur.fetchall())
cur.close()
conn.close()

