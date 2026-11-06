import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'iam' AND table_name = 'users';")
print('iam.users columns:', [r[0] for r in cur.fetchall()])

cur.execute("SELECT * FROM iam.users;")
users = cur.fetchall()
for u in users:
    print('User:', u)

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'iam' AND table_name = 'user_roles';")
print('iam.user_roles columns:', [r[0] for r in cur.fetchall()])

cur.execute("SELECT * FROM iam.user_roles;")
print('iam.user_roles rows:', cur.fetchall())

cur.execute("SELECT * FROM iam.roles;")
print('iam.roles rows:', cur.fetchall())

