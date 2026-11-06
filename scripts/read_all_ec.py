import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT election_center_id, tenant_id, election_id, center_id FROM polling.election_centers;")
print("Rows in polling.election_centers:", cur.fetchall())
cur.close()
conn.close()

