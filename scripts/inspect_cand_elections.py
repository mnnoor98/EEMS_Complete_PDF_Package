import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false);")

cur.execute('SELECT candidate_id, name, is_active FROM election.candidates;')
for c in cur.fetchall():
    print('Cand:', c)

print('\nCandidate Elections:')
cur.execute('''
    SELECT ce.candidate_election_id, ce.candidate_id, ce.election_id, c.name, ce.is_active, ce.party_name, s.name_bn
    FROM election.candidate_elections ce
    JOIN election.candidates c ON ce.candidate_id = c.candidate_id
    LEFT JOIN election.symbols s ON ce.symbol_id = s.symbol_id;
''')
for ce in cur.fetchall():
    print('CE:', ce)

