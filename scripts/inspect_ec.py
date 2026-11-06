import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
cur.execute("""
    SELECT c.center_id, c.name, c.code, b.booth_id, b.name, b.code
    FROM polling.election_centers ec
    JOIN polling.centers c ON c.center_id = ec.center_id
    LEFT JOIN polling.booths b ON b.center_id = c.center_id
    WHERE ec.election_id = %s
    ORDER BY c.code, b.code;
""", (ELECTION_ID,))
rows = cur.fetchall()
print(f"Total center-booths: {len(rows)}")
for r in rows[:6]:
    print(r)
cur.close()
conn.close()

