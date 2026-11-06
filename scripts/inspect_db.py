import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false)")

print('=== USERS in iam schema ===')
cur.execute('SELECT * FROM iam.users')
cols = [desc[0] for desc in cur.description]
print(cols)
for r in cur.fetchall():
    print(r)

print('=== TENANT USERS ===')
cur.execute('SELECT * FROM iam.tenant_users')
cols = [desc[0] for desc in cur.description]
print(cols)
for r in cur.fetchall():
    print(r)

print('\n=== ALL CANDIDATES in election.candidates ===')
cur.execute('SELECT candidate_id, name, party_name_bn, party_name_en FROM election.candidates')
for r in cur.fetchall():
    print(r)

print('\n=== FOREIGN KEYS TO results.submissions ===')
cur.execute('''
    SELECT tc.table_schema, tc.table_name, kcu.column_name, ccu.table_schema AS foreign_table_schema, ccu.table_name AS foreign_table_name, rc.delete_rule
    FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.referential_constraints AS rc
      ON tc.constraint_name = rc.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = rc.constraint_name
    WHERE ccu.table_name = 'submissions';
''')
for r in cur.fetchall():
    print(r)

conn.close()
