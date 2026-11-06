-- Migration: Add candidate scoping to tenant_users, voters, and incidents
SET app.tenant_id = '704c25fe-4422-4960-8907-49ccaedd309b';

DO $$
BEGIN
    -- 1. Add candidate_id to iam.tenant_users
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'iam' AND table_name = 'tenant_users' AND column_name = 'candidate_id'
    ) THEN
        ALTER TABLE iam.tenant_users ADD COLUMN candidate_id UUID NULL REFERENCES election.candidates(candidate_id) ON DELETE SET NULL;
        CREATE INDEX IF NOT EXISTS idx_tenant_users_candidate ON iam.tenant_users(tenant_id, candidate_id);
    END IF;

    -- 2. Add candidate_id to polling.voters
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'polling' AND table_name = 'voters' AND column_name = 'candidate_id'
    ) THEN
        ALTER TABLE polling.voters ADD COLUMN candidate_id UUID NULL REFERENCES election.candidates(candidate_id) ON DELETE SET NULL;
        CREATE INDEX IF NOT EXISTS idx_voters_candidate ON polling.voters(tenant_id, candidate_id);
    END IF;

    -- 3. Add candidate_id to polling.incidents
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'polling' AND table_name = 'incidents' AND column_name = 'candidate_id'
    ) THEN
        ALTER TABLE polling.incidents ADD COLUMN candidate_id UUID NULL REFERENCES election.candidates(candidate_id) ON DELETE SET NULL;
        CREATE INDEX IF NOT EXISTS idx_incidents_candidate ON polling.incidents(tenant_id, candidate_id);
    END IF;
END $$;

-- Update existing seed voters and incidents to link to primary candidate
UPDATE polling.voters 
SET candidate_id = 'c6522262-66f9-4e68-b76f-b8f69167f5cc'
WHERE candidate_id IS NULL;

UPDATE polling.incidents 
SET candidate_id = 'c6522262-66f9-4e68-b76f-b8f69167f5cc'
WHERE candidate_id IS NULL;

-- Assign candidate to user 'tousif' for demonstration, while 'admin' remains Super Admin (candidate_id IS NULL)
UPDATE iam.tenant_users
SET candidate_id = 'c6522262-66f9-4e68-b76f-b8f69167f5cc'
WHERE user_id = (SELECT user_id FROM iam.users WHERE external_subject = 'tousif');
