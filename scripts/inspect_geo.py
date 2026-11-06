import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false);")
cur.execute("SELECT election_id, name, area_id FROM election.elections WHERE election_id = 'eade9993-71f5-4bbc-b92c-b636333a2714'::uuid;")
print("Election area:", cur.fetchall())
cur.close()
conn.close()
