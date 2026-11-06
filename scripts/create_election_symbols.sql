SET client_encoding = 'UTF8';

-- 1. Create Electoral Symbols Catalog Table
CREATE TABLE IF NOT EXISTS election.symbols (
    symbol_id SERIAL PRIMARY KEY,
    code VARCHAR(40) UNIQUE NOT NULL,
    name_bn VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    category VARCHAR(40) NOT NULL,
    icon_emoji VARCHAR(20) NOT NULL DEFAULT '🗳️',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. Seed Official Bangladesh Election Commission Symbols
INSERT INTO election.symbols (code, name_bn, name_en, category, icon_emoji) VALUES
-- Parliamentary & Major Parties
('BOAT', 'নৌকা', 'Boat', 'POLITICAL_PARTY', '⛵'),
('SHEAF_OF_PADDY', 'ধানের শীষ', 'Sheaf of Paddy', 'POLITICAL_PARTY', '🌾'),
('PLOW', 'লাঙ্গল', 'Plow', 'POLITICAL_PARTY', '🚜'),
('SCALES', 'দাঁড়িপাল্লা', 'Scales', 'POLITICAL_PARTY', '⚖️'),
('HAND_FAN', 'হাতপাখা', 'Hand Fan', 'POLITICAL_PARTY', '🪭'),
('TORCH', 'মশাল', 'Torch', 'POLITICAL_PARTY', '🔥'),
('STAR', 'তারা', 'Star', 'POLITICAL_PARTY', '⭐'),
('ROSE', 'গোলাপ ফুল', 'Rose', 'POLITICAL_PARTY', '🌹'),
('HURRICANE', 'হারিকেন', 'Lantern', 'POLITICAL_PARTY', '🏮'),
('LADDER', 'মই', 'Ladder', 'POLITICAL_PARTY', '🪜'),

-- Independent & Local Government (Upazila / City / Union)
('PINEAPPLE', 'আনারস', 'Pineapple', 'INDEPENDENT', '🍍'),
('FOOTBALL', 'ফুটবল', 'Football', 'INDEPENDENT', '⚽'),
('CUP_SAUCER', 'কাপ-পিরিচ', 'Cup & Saucer', 'INDEPENDENT', '☕'),
('PITCHER', 'কলস', 'Pitcher (Kolos)', 'INDEPENDENT', '🏺'),
('MOTORCYCLE', 'মোটরসাইকেল', 'Motorcycle', 'INDEPENDENT', '🏍️'),
('HORSE', 'ঘোড়া', 'Horse', 'INDEPENDENT', '🐴'),
('RICKSHAW', 'রিকশা', 'Rickshaw', 'INDEPENDENT', '🛺'),
('INKPOT_PEN', 'দোয়াত-কলম', 'Inkpot & Pen', 'INDEPENDENT', '🖋️'),
('HELMET', 'হেলমেট', 'Helmet', 'INDEPENDENT', '⛑️'),
('SHRIMP', 'চিংড়ি মাছ', 'Shrimp', 'INDEPENDENT', '🦐'),
('TELEPHONE', 'টেলিফোন', 'Telephone', 'INDEPENDENT', '☎️'),
('BICYCLE', 'বাইসাইকেল', 'Bicycle', 'INDEPENDENT', '🚲'),
('WRIST_WATCH', 'হাতঘড়ি', 'Wrist Watch', 'INDEPENDENT', '⌚'),
('AIRPLANE', 'উড়োজাহাজ', 'Airplane', 'INDEPENDENT', '✈️'),
('LOCKET', 'তালা', 'Lock', 'INDEPENDENT', '🔒'),
('BAT', 'ক্রিকেট ব্যাট', 'Cricket Bat', 'INDEPENDENT', '🏏'),
('CHAIR', 'চেয়ার', 'Chair', 'INDEPENDENT', '🪑'),
('CAR', 'কার / মোটরগাড়ি', 'Motor Car', 'INDEPENDENT', '🚗')
ON CONFLICT (code) DO UPDATE 
SET name_bn = EXCLUDED.name_bn,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    icon_emoji = EXCLUDED.icon_emoji;

-- 3. Extend election.candidates table with candidate campaign & symbol fields
ALTER TABLE election.candidates 
    ADD COLUMN IF NOT EXISTS symbol_id INTEGER REFERENCES election.symbols(symbol_id),
    ADD COLUMN IF NOT EXISTS party_name_bn VARCHAR(150),
    ADD COLUMN IF NOT EXISTS party_name_en VARCHAR(150),
    ADD COLUMN IF NOT EXISTS slogan VARCHAR(300),
    ADD COLUMN IF NOT EXISTS phone VARCHAR(30),
    ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500),
    ADD COLUMN IF NOT EXISTS campaign_office VARCHAR(300);

-- 4. Extend election.candidate_elections with assigned symbol and party for that election
ALTER TABLE election.candidate_elections
    ADD COLUMN IF NOT EXISTS symbol_id INTEGER REFERENCES election.symbols(symbol_id),
    ADD COLUMN IF NOT EXISTS party_name VARCHAR(150),
    ADD COLUMN IF NOT EXISTS slogan VARCHAR(300);
