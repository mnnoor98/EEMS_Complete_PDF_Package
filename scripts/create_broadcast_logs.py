import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

create_table_sql = """
CREATE TABLE IF NOT EXISTS campaign.broadcast_logs (
    broadcast_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    election_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL DEFAULT 'SMS',
    recipient_group VARCHAR(50) NOT NULL DEFAULT 'POLLING_AGENTS',
    recipient_count INT NOT NULL DEFAULT 1,
    message_content TEXT NOT NULL,
    template_type VARCHAR(50) NULL,
    sent_by_user_id UUID NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'DELIVERED'
);
"""

cur.execute(create_table_sql)
conn.commit()
print("campaign.broadcast_logs created successfully!")

# Seed 2 realistic broadcast logs so the UI shows immediate operational history!
seed_logs_sql = """
INSERT INTO campaign.broadcast_logs (tenant_id, election_id, channel, recipient_group, recipient_count, message_content, template_type, status, sent_at)
SELECT 
    '704c25fe-4422-4960-8907-49ccaedd309b'::uuid,
    'eade9993-71f5-4bbc-b92c-b636333a2714'::uuid,
    'SMS',
    'POLLING_AGENTS',
    2,
    'প্রিয় পোলিং এজেন্ট, সকাল ৭:৩০ এর মধ্যে স্ব স্ব কেন্দ্রের বুথে প্রবেশ করুন ও ব্যালট বাক্স পরীক্ষা করে সিল নিশ্চিত করুন। - ডঃ কাজী উবায়েদ উল্লাহ ফারুক (দাঁড়িপাল্লা)',
    'MORNING_CHECKIN',
    'DELIVERED',
    NOW() - INTERVAL '3 hours'
WHERE NOT EXISTS (SELECT 1 FROM campaign.broadcast_logs WHERE template_type = 'MORNING_CHECKIN');

INSERT INTO campaign.broadcast_logs (tenant_id, election_id, channel, recipient_group, recipient_count, message_content, template_type, status, sent_at)
SELECT 
    '704c25fe-4422-4960-8907-49ccaedd309b'::uuid,
    'eade9993-71f5-4bbc-b92c-b636333a2714'::uuid,
    'WHATSAPP',
    'POLLING_AGENTS',
    2,
    'ভোট গণনা শেষ না হওয়া পর্যন্ত কেন্দ্র ত্যাগ করবেন না। প্রিজাইডিং অফিসারের স্বাক্ষরিত ফরম-৮ এর ছবি অবিলম্বে হোয়াটসঅ্যাপে পাঠান। - প্রধান নির্বাচনী এজেন্ট',
    'FORM8_REMINDER',
    'DELIVERED',
    NOW() - INTERVAL '1 hour'
WHERE NOT EXISTS (SELECT 1 FROM campaign.broadcast_logs WHERE template_type = 'FORM8_REMINDER');
"""

cur.execute(seed_logs_sql)
conn.commit()

cur.execute("SELECT broadcast_id, channel, recipient_count, template_type, status, sent_at FROM campaign.broadcast_logs;")
for r in cur.fetchall():
    print("Log row:", r)

cur.close()
conn.close()

