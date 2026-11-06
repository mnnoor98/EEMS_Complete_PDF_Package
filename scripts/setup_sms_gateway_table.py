import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS campaign.sms_gateway_configs (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    election_id UUID NOT NULL,
    provider VARCHAR(50) NOT NULL DEFAULT 'SIMULATOR',
    api_key VARCHAR(255) NOT NULL DEFAULT '',
    api_secret VARCHAR(255) NULL,
    sender_id VARCHAR(50) NULL DEFAULT 'EEMS_NOTICE',
    endpoint_url VARCHAR(500) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_tested_at TIMESTAMPTZ NULL,
    balance NUMERIC(10,2) NOT NULL DEFAULT 5000.00,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_sms_config_tenant_election UNIQUE (tenant_id, election_id)
);
""")

TENANT_ID = '704c25fe-4422-4960-8907-49ccaedd309b'
ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'

cur.execute("""
INSERT INTO campaign.sms_gateway_configs (tenant_id, election_id, provider, api_key, sender_id, endpoint_url, balance)
VALUES (%s, %s, 'SIMULATOR', 'sim_api_key_demo_2026', 'SCALE_FARUK', 'http://api.greenweb.com.bd/api.php', 2500.00)
ON CONFLICT (tenant_id, election_id) DO UPDATE 
SET updated_at = NOW();
""", (TENANT_ID, ELECTION_ID))

conn.commit()
print("Table campaign.sms_gateway_configs created and default config inserted successfully.")
cur.close()
conn.close()

