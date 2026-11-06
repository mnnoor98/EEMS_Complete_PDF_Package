import psycopg2

conn = psycopg2.connect('postgresql://eems_app:123456@localhost:5432/eems_dev')
cur = conn.cursor()
cur.execute("SELECT set_config('app.tenant_id', '704c25fe-4422-4960-8907-49ccaedd309b', false);")

cur.execute("""
    SELECT c.candidate_id, c.name, ce.election_id, s.name_bn, s.icon_emoji, ce.party_name, c.phone, c.campaign_office, el.name as election_name
    FROM election.candidates c
    JOIN election.candidate_elections ce ON c.candidate_id = ce.candidate_id
    LEFT JOIN election.symbols s ON ce.symbol_id = s.symbol_id
    LEFT JOIN election.elections el ON ce.election_id = el.election_id
    WHERE c.is_active = TRUE
    ORDER BY ce.created_at;
""")
cands = cur.fetchall()
print('Total Candidates in Election:', len(cands))
for row in cands:
    cid = row[0]
    cur.execute('SELECT COUNT(*) FROM polling.booth_agents WHERE candidate_id = %s;', (cid,))
    agents = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*), COUNT(*) FILTER (WHERE slip_issued = TRUE) FROM polling.voters WHERE candidate_id = %s;', (cid,))
    voters, slips = cur.fetchone()
    cur.execute('SELECT COUNT(*) FROM iam.tenant_users WHERE candidate_id = %s;', (cid,))
    team = cur.fetchone()[0]
    cur.execute("""
        SELECT u.external_subject, u.display_name 
        FROM iam.tenant_users tu 
        JOIN iam.users u ON tu.user_id = u.user_id 
        WHERE tu.candidate_id = %s 
        ORDER BY tu.joined_at 
        LIMIT 1;
    """, (cid,))
    assigned_user = cur.fetchone()
    u_str = f"{assigned_user[0]} ({assigned_user[1]})" if assigned_user else "অ্যাসাইন বাকি"
    
    cur.execute("""
        SELECT COALESCE(SUM(d.votes), 0)
        FROM results.details d
        JOIN election.candidate_elections sub_ce ON d.candidate_election_id = sub_ce.candidate_election_id
        WHERE sub_ce.candidate_id = %s;
    """, (cid,))
    votes = cur.fetchone()[0]

    print(f"👉 Candidate: {row[1]} | Symbol: {row[4]} {row[3]} | User: {u_str} | Team: {team} | Agents: {agents} | Voters: {voters} (Slips: {slips}) | Total Votes: {votes}")
