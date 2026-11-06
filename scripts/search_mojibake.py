import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false)")

cur.execute("""
    SELECT table_schema, table_name, column_name 
    FROM information_schema.columns 
    WHERE data_type IN ('text', 'character varying') 
      AND table_schema NOT IN ('pg_catalog', 'information_schema')
""")
text_cols = cur.fetchall()

print(f'Checking {len(text_cols)} columns across database...')
found = []
for schema, table, col in text_cols:
    try:
        cur.execute(f"SELECT {col} FROM {schema}.{table} WHERE {col} LIKE '%à¦%' LIMIT 5")
        rows = cur.fetchall()
        if rows:
            found.append((schema, table, col, rows))
    except Exception as e:
        conn.rollback()
        cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false)")

print(f'Found {len(found)} columns with mojibake:')
for schema, table, col, rows in found:
    print(f'  {schema}.{table}.{col}: {rows}')

conn.close()

