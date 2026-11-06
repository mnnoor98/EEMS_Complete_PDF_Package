import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'polling' AND table_name = 'voters' ORDER BY ordinal_position;")
print("=== polling.voters ===")
for r in cur.fetchall():
    print(r)

cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'campaign' AND table_name = 'broadcast_logs' ORDER BY ordinal_position;")
print("\n=== campaign.broadcast_logs ===")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()

