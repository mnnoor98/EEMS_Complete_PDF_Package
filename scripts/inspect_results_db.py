import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false)")

print('=== SUBMISSIONS FOR ELECTION ===')
cur.execute("""
    SELECT submission_id, election_center_id, declared_total_votes, submission_state_id, created_at 
    FROM results.submissions
    WHERE election_id = 'eade9993-71f5-4bbc-b92c-b636333a2714'
""")
for r in cur.fetchall():
    print(r)

print('=== VERIFICATIONS ===')
cur.execute("SELECT * FROM results.verifications")
for r in cur.fetchall():
    print(r)

print('=== DOCUMENTS ===')
cur.execute("SELECT * FROM results.documents")
for r in cur.fetchall():
    print(r)

conn.close()

