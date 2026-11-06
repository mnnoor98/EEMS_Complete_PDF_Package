import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false)")

cur.execute("""
    SELECT c.candidate_id, c.name, c.party_name_bn, ce.party_name
    FROM election.candidates c
    LEFT JOIN election.candidate_elections ce ON c.candidate_id = ce.candidate_id
    WHERE c.candidate_id = 'e2fff660-830e-40a9-ab69-edbf8473e55d'
""")
row = cur.fetchone()
print('Candidate ID:', row[0])
print('c.name:', repr(row[1]))
print('c.name bytes:', [hex(b) for b in row[1].encode('utf-8')])
print('c.party_name_bn:', repr(row[2]))
print('ce.party_name:', repr(row[3]))

conn.close()
