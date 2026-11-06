-- ====================================================================
-- EEMS: Candidate Polling Agent Management Schema
-- ====================================================================

CREATE TABLE IF NOT EXISTS polling.booth_agents (
    booth_agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
    election_id UUID NOT NULL REFERENCES election.elections(election_id) ON DELETE CASCADE,
    center_id UUID NOT NULL REFERENCES polling.centers(center_id) ON DELETE CASCADE,
    booth_id UUID NOT NULL REFERENCES polling.booths(booth_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES election.candidates(candidate_id) ON DELETE CASCADE,
    agent_type VARCHAR(20) NOT NULL DEFAULT 'PRIMARY', -- 'PRIMARY' (মূল), 'RESERVE' (বিকল্প)
    full_name VARCHAR(150) NOT NULL,
    nid_number VARCHAR(30) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    voter_number VARCHAR(50),
    photo_url VARCHAR(500),
    appointment_letter_issued BOOLEAN NOT NULL DEFAULT FALSE,
    checked_in_at_booth TIMESTAMPTZ NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ASSIGNED', -- 'ASSIGNED', 'PRESENT', 'ABSENT', 'EXPELLED'
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for lightning-fast queries during election day operations
CREATE INDEX IF NOT EXISTS idx_booth_agents_election ON polling.booth_agents(tenant_id, election_id);
CREATE INDEX IF NOT EXISTS idx_booth_agents_center ON polling.booth_agents(center_id);
CREATE INDEX IF NOT EXISTS idx_booth_agents_booth ON polling.booth_agents(booth_id);
CREATE INDEX IF NOT EXISTS idx_booth_agents_candidate ON polling.booth_agents(candidate_id);

-- Enable Row Level Security (RLS)
ALTER TABLE polling.booth_agents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_booth_agents ON polling.booth_agents;
CREATE POLICY tenant_isolation_booth_agents ON polling.booth_agents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);

-- Seed initial booth agents for testing
DO $$
DECLARE
    v_tenant_id UUID;
    v_election_id UUID;
    v_candidate_id UUID;
    v_center_id UUID;
    v_booth_1 UUID;
    v_booth_2 UUID;
BEGIN
    SELECT tenant_id INTO v_tenant_id FROM core.tenants WHERE code = '1000000000' LIMIT 1;
    IF v_tenant_id IS NULL THEN
        SELECT tenant_id INTO v_tenant_id FROM core.tenants LIMIT 1;
    END IF;

    SELECT election_id INTO v_election_id FROM election.elections WHERE tenant_id = v_tenant_id LIMIT 1;
    SELECT candidate_id INTO v_candidate_id FROM election.candidates WHERE tenant_id = v_tenant_id LIMIT 1;
    
    SELECT c.center_id INTO v_center_id 
    FROM polling.election_centers ec
    JOIN polling.centers c ON ec.center_id = c.center_id
    WHERE ec.tenant_id = v_tenant_id AND ec.election_id = v_election_id
    LIMIT 1;

    IF v_center_id IS NOT NULL THEN
        SELECT booth_id INTO v_booth_1 FROM polling.booths WHERE center_id = v_center_id ORDER BY code LIMIT 1;
        SELECT booth_id INTO v_booth_2 FROM polling.booths WHERE center_id = v_center_id ORDER BY code OFFSET 1 LIMIT 1;

        IF v_booth_1 IS NOT NULL AND v_candidate_id IS NOT NULL THEN
            INSERT INTO polling.booth_agents (
                tenant_id, election_id, center_id, booth_id, candidate_id, 
                agent_type, full_name, nid_number, phone, voter_number, appointment_letter_issued, status
            ) VALUES (
                v_tenant_id, v_election_id, v_center_id, v_booth_1, v_candidate_id,
                'PRIMARY', 'মোহাম্মদ রফিকুল ইসলাম', '19852691234567890', '01711223344', 'VOT-10492', TRUE, 'PRESENT'
            ) ON CONFLICT DO NOTHING;
        END IF;

        IF v_booth_2 IS NOT NULL AND v_candidate_id IS NOT NULL THEN
            INSERT INTO polling.booth_agents (
                tenant_id, election_id, center_id, booth_id, candidate_id, 
                agent_type, full_name, nid_number, phone, voter_number, appointment_letter_issued, status
            ) VALUES (
                v_tenant_id, v_election_id, v_center_id, v_booth_2, v_candidate_id,
                'PRIMARY', 'নাজমিন আক্তার', '19902699876543210', '01819887766', 'VOT-10493', TRUE, 'ASSIGNED'
            ) ON CONFLICT DO NOTHING;
        END IF;
    END IF;
END $$;
