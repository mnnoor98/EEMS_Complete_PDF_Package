import psycopg2, uuid

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
CANDIDATE_ID = 'e2fff660-830e-40a9-ab69-edbf8473e55d'
TENANT_ID = '704c25fe-4422-4960-8907-49ccaedd309b'

cur.execute("SELECT id, name, code FROM polling.centers WHERE election_id = %s ORDER BY code;", (ELECTION_ID,))
centers = cur.fetchall()
print(f"Found {len(centers)} centers:")
for c in centers:
    print(c)

cur.execute("SELECT id, center_id, name, code FROM polling.booths WHERE center_id = %s;", (centers[0][0],))
booths = cur.fetchall()
print(f"Booths in first center {centers[0][1]}:")
for b in booths:
    print(b)

cur.close()
conn.close()

