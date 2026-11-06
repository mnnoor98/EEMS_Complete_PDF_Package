-- Create polling.voters and polling.incidents tables

CREATE TABLE IF NOT EXISTS polling.voters (
    voter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
    election_id UUID NOT NULL REFERENCES election.elections(election_id) ON DELETE CASCADE,
    center_id UUID NOT NULL REFERENCES polling.centers(center_id) ON DELETE CASCADE,
    booth_id UUID NULL REFERENCES polling.booths(booth_id) ON DELETE SET NULL,
    voter_number VARCHAR(50) NOT NULL,
    serial_number INT NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    father_or_spouse_name VARCHAR(150) NULL,
    gender VARCHAR(10) NOT NULL DEFAULT 'MALE',
    age INT NULL,
    area_name VARCHAR(150) NULL,
    category VARCHAR(30) NOT NULL DEFAULT 'SUPPORTER',
    slip_issued BOOLEAN NOT NULL DEFAULT FALSE,
    has_voted BOOLEAN NOT NULL DEFAULT FALSE,
    phone VARCHAR(20) NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE polling.voters ENABLE ROW LEVEL SECURITY;
ALTER TABLE polling.voters FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_voters ON polling.voters;
CREATE POLICY tenant_isolation_voters ON polling.voters
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

CREATE INDEX IF NOT EXISTS idx_voters_election ON polling.voters(tenant_id, election_id);
CREATE INDEX IF NOT EXISTS idx_voters_center ON polling.voters(center_id);
CREATE INDEX IF NOT EXISTS idx_voters_serial ON polling.voters(election_id, center_id, serial_number);

CREATE TABLE IF NOT EXISTS polling.incidents (
    incident_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
    election_id UUID NOT NULL REFERENCES election.elections(election_id) ON DELETE CASCADE,
    center_id UUID NOT NULL REFERENCES polling.centers(center_id) ON DELETE CASCADE,
    booth_id UUID NULL REFERENCES polling.booths(booth_id) ON DELETE SET NULL,
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'HIGH',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    reported_by VARCHAR(150) NOT NULL,
    reported_by_phone VARCHAR(30) NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(30) NOT NULL DEFAULT 'REPORTED',
    evidence_attachment_url VARCHAR(500) NULL,
    magistrate_name VARCHAR(150) NULL,
    action_taken TEXT NULL,
    official_complaint_generated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE polling.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE polling.incidents FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_incidents ON polling.incidents;
CREATE POLICY tenant_isolation_incidents ON polling.incidents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

CREATE INDEX IF NOT EXISTS idx_incidents_election ON polling.incidents(tenant_id, election_id);
CREATE INDEX IF NOT EXISTS idx_incidents_center ON polling.incidents(center_id);

-- Seed initial voters and sample incident for Demo Election
SET app.tenant_id = '704c25fe-4422-4960-8907-49ccaedd309b';

INSERT INTO polling.voters (
    voter_id, tenant_id, election_id, center_id, booth_id,
    voter_number, serial_number, full_name, father_or_spouse_name,
    gender, age, area_name, category, slip_issued, has_voted, phone, notes
)
VALUES
(
    'a1111111-1111-1111-1111-111111111101',
    '704c25fe-4422-4960-8907-49ccaedd309b',
    '7a2ec4ed-9aba-4707-aa49-a58b51e82713',
    'ff36afed-ff27-43d6-88de-d6292e3098bd',
    'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
    '269123450001', 1, 'আব্দুল কাদের', 'মরহুম রহমান আলী',
    'MALE', 52, 'দোহার বাজার পাড়া', 'SUPPORTER', true, false, '01711223344', 'বিশ্বস্ত ভোটার ও পরিবার প্রধান'
),
(
    'a1111111-1111-1111-1111-111111111102',
    '704c25fe-4422-4960-8907-49ccaedd309b',
    '7a2ec4ed-9aba-4707-aa49-a58b51e82713',
    'ff36afed-ff27-43d6-88de-d6292e3098bd',
    'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
    '269123450002', 2, 'রাবেয়া খাতুন', 'আব্দুল কাদের',
    'FEMALE', 46, 'দোহার বাজার পাড়া', 'SUPPORTER', true, false, '01711223345', 'মহিলা উইং সদস্য'
),
(
    'a1111111-1111-1111-1111-111111111103',
    '704c25fe-4422-4960-8907-49ccaedd309b',
    '7a2ec4ed-9aba-4707-aa49-a58b51e82713',
    'ff36afed-ff27-43d6-88de-d6292e3098bd',
    'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
    '269123450003', 3, 'কামরুল হাসান সজীব', 'আব্দুল কাদের',
    'MALE', 24, 'দোহার বাজার পাড়া', 'SUPPORTER', false, false, '01819556677', 'নতুন যুব ভোটার'
),
(
    'a1111111-1111-1111-1111-111111111104',
    '704c25fe-4422-4960-8907-49ccaedd309b',
    '7a2ec4ed-9aba-4707-aa49-a58b51e82713',
    'ff36afed-ff27-43d6-88de-d6292e3098bd',
    'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
    '269123450004', 4, 'ফারহানা ইসলাম তমা', 'মোঃ আমিনুল ইসলাম',
    'FEMALE', 28, 'দোহার কলেজ রোড', 'SWING', false, false, '01911443322', 'শিক্ষক, নিরপেক্ষ দৃষ্টিভঙ্গি'
)
ON CONFLICT (voter_id) DO NOTHING;

INSERT INTO polling.incidents (
    incident_id, tenant_id, election_id, center_id, booth_id,
    incident_type, severity, title, description,
    reported_by, reported_by_phone, reported_at, status,
    evidence_attachment_url, magistrate_name, action_taken, official_complaint_generated
)
VALUES
(
    'c1111111-1111-1111-1111-111111111101',
    '704c25fe-4422-4960-8907-49ccaedd309b',
    '7a2ec4ed-9aba-4707-aa49-a58b51e82713',
    'ff36afed-ff27-43d6-88de-d6292e3098bd',
    'cb6df0b5-ed1e-4b38-b1e2-891194bc6f39',
    'BOOTH_AGENT_EXPELLED',
    'CRITICAL',
    '১ নং বুথ থেকে পোলিং এজেন্টকে জোরপূর্বক বের করে দেওয়ার চেষ্টা',
    'সকাল ৮:১৫ ঘটিকায় প্রতিপক্ষ প্রার্থীর সমর্থকরা ১ নং বুথে প্রবেশ করে আমাদের নিয়োজিত পোলিং এজেন্ট মোহাম্মদ রফিকুল ইসলামকে হুমকি প্রদর্শন করে ও বুথ থেকে বের করে দেওয়ার চেষ্টা চালায়।',
    'মোহাম্মদ রফিকুল ইসলাম (পোলিং এজেন্ট)',
    '01712345678',
    NOW() - INTERVAL '2 hours',
    'SUBMITTED_TO_EC',
    '/evidence/incident_c01_b01.jpg',
    'মোঃ জাহিদুল ইসলাম (নির্বাহী ম্যাজিস্ট্রেট)',
    'ম্যাজিস্ট্রেট ও স্ট্রাইকিং ফোর্স কেন্দ্রে উপস্থিত হয়ে নিরাপত্তা জোরদার করেছেন এবং এজেন্টের অবস্থান নিশ্চিত করেছেন।',
    true
)
ON CONFLICT (incident_id) DO NOTHING;
