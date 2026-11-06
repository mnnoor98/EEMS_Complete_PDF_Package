import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'iam';")
print('IAM tables:', [r[0] for r in cur.fetchall()])

for tbl in ['permissions', 'roles', 'role_permissions', 'user_roles']:
    cur.execute(f"SELECT COUNT(*) FROM iam.{tbl};")
    print(f"iam.{tbl} count:", cur.fetchone()[0])

