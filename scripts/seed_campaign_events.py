import psycopg2, uuid

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()

tenant_id = '704c25fe-4422-4960-8907-49ccaedd309b'
election_id = 'eade9993-71f5-4bbc-b92c-b636333a2714'
area_id = 4  # Valid area_id for this election

# Set RLS Tenant Context
cur.execute("SELECT set_config('app.tenant_id', %s, false);", (tenant_id,))

# 1. Create venues
venues_data = [
    ('ইয়াকুবপুর বাজার কেন্দ্রীয় মাঠ', 'ইয়াকুবপুর বাজার, দাগনভূঞা, ফেনী', 5000),
    ('বরইয়া আলী আকবর উচ্চ বিদ্যালয় অডিটোরিয়াম', 'বরইয়া, দাগনভূঞা, ফেনী', 1500),
    ('দাগনভূঞা বাস টার্মিনাল চত্বর', 'দাগনভূঞা প্রধান সড়ক ও বাস টার্মিনাল', 3500),
    ('মৌলভীবাজার সরকারি প্রাথমিক বিদ্যালয় প্রাঙ্গণ', 'মৌলভীবাজার, দাগনভূঞা', 2000)
]

venue_ids = []
for name, addr, cap in venues_data:
    cur.execute("SELECT venue_id FROM campaign.venues WHERE tenant_id = %s AND name = %s;", (tenant_id, name))
    row = cur.fetchone()
    if row:
        venue_ids.append(row[0])
    else:
        v_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO campaign.venues (venue_id, tenant_id, area_id, name, address, capacity, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, true);
        """, (v_id, tenant_id, area_id, name, addr, cap))
        venue_ids.append(v_id)

conn.commit()
print("Venues seeded:", len(venue_ids))

# 2. Seed Campaign Events and Permits
events_data = [
    (
        'ইয়াকুবপুর ইউনিয়ন কেন্দ্রীয় নির্বাচনী জনসভা ও পথসমাবেশ',
        1,  # RALLY
        1,  # PLANNED
        venue_ids[0],
        '2026-11-22 15:00:00+06',
        '2026-11-22 18:30:00+06',
        'কেন্দ্রীয় জনসভা ও প্রার্থীর নির্বাচনী ইশতেহার ঘোষণা',
        'দাগন-থানা/নির্বাচন-অনুমতি/২০২৬/১১২',
        'অফিসার ইনচার্জ (ওসি), দাগনভূঞা থানা',
        2  # APPROVED
    ),
    (
        'ওয়ার্ড নং ১ ও ২ যুব ও নারী কর্মী সম্মেলন এবং উঠান বৈঠক',
        2,  # MEETING
        1,  # PLANNED
        venue_ids[1],
        '2026-11-23 10:00:00+06',
        '2026-11-23 13:00:00+06',
        'ভোটকেন্দ্রভিত্তিক কর্মী পরিচালনা ও ভোটার স্লিপ বিতরণ পরিকল্পনা',
        'উপজেলা-প্রশাসন/ইউএনও/পারমিট/০৮',
        'সহকারী রিটার্নিং অফিসার ও ইউএনও',
        2  # APPROVED
    ),
    (
        'দাগনভূঞা প্রধান সড়কে মাইকিং রোডশো ও লিফলেট বিতরণ কর্মসূচি',
        1,  # RALLY
        1,  # PLANNED
        venue_ids[2],
        '2026-11-24 09:00:00+06',
        '2026-11-24 17:00:00+06',
        'সকাল ৯টা থেকে বিকেল ৫টা পর্যন্ত অনুমোদিত মাইকিং রুট',
        'দাগন-থানা/আবেদন-অপেক্ষমান/৭৭',
        'দাগনভূঞা থানা পুলিশ',
        1  # PENDING
    )
]

for title, type_id, state_id, venue_id, start_t, end_t, report, p_ref, p_auth, p_state in events_data:
    cur.execute("SELECT event_id FROM campaign.events WHERE tenant_id = %s AND election_id = %s AND title = %s;", (tenant_id, election_id, title))
    row = cur.fetchone()
    if not row:
        ev_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO campaign.events (event_id, tenant_id, election_id, event_type_id, event_state_id, area_id, venue_id, title, starts_at, ends_at, completion_report, created_at, version)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1);
        """, (ev_id, tenant_id, election_id, type_id, state_id, area_id, venue_id, title, start_t, end_t, report))

        # create permit
        permit_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO campaign.permits (permit_id, tenant_id, event_id, permit_state_id, issuing_authority, reference_number, expires_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (permit_id, tenant_id, ev_id, p_state, p_auth, p_ref, '2026-11-30'))

conn.commit()

cur.execute("""
    SELECT e.event_id, e.title, et.name, es.name, v.name, p.reference_number, ps.name, e.starts_at, e.ends_at 
    FROM campaign.events e
    JOIN campaign.event_types et ON e.event_type_id = et.event_type_id
    JOIN campaign.event_states es ON e.event_state_id = es.event_state_id
    LEFT JOIN campaign.venues v ON e.venue_id = v.venue_id
    LEFT JOIN campaign.permits p ON e.event_id = p.event_id
    LEFT JOIN campaign.permit_states ps ON p.permit_state_id = ps.permit_state_id
    WHERE e.tenant_id = %s AND e.election_id = %s;
""", (tenant_id, election_id))

print("\n=== CURRENT SEEDED CAMPAIGN EVENTS & PERMITS ===")
for r in cur.fetchall():
    print(" -", r)

cur.close()
conn.close()
