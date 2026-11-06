import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false)")

cur.execute("""
    SELECT c.center_id, c.code, c.name, ec.election_center_id, ec.election_id
    FROM polling.centers c
    LEFT JOIN polling.election_centers ec ON c.center_id = ec.center_id
    WHERE c.name LIKE '%বরইয়া%' OR c.code = 'C-101'
""")
for r in cur.fetchall():
    print(r)

conn.close()

