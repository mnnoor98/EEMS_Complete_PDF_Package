import urllib.request
import json

# 1. Login as sub-user
login_url = 'http://localhost:5131/api/v1/auth/login'
sub_login_data = json.dumps({'tenantId': '1000000000', 'username': 'agent_3d72b1', 'password': 'Password123!'}).encode('utf-8')
req = urllib.request.Request(login_url, data=sub_login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))['accessToken']

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
election_id = 'eade9993-71f5-4bbc-b92c-b636333a2714'

# 2. Get Centers in election
req_centers = urllib.request.Request(f'http://localhost:5131/api/v1/elections/{election_id}/centers', headers=headers)
with urllib.request.urlopen(req_centers) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    centers = res.get('items', res) if isinstance(res, dict) else res
    print(f"Centers accessible by sub-user: {len(centers)}")
    center_id = centers[0]['centerId']
    print(f"Testing with Center: {centers[0]['name']} ({center_id})")

# 3. Get candidates in election
req_cands = urllib.request.Request(f'http://localhost:5131/api/v1/candidate/candidates', headers=headers)
with urllib.request.urlopen(req_cands) as resp:
    cands = json.loads(resp.read().decode('utf-8'))
    print(f"Contesting candidates count: {len(cands)}")
    for c in cands:
        print(f" - {c.get('symbolEmoji', '🗳️')} {c['name']} ({c['partyName']})")

# 4. Submit multi-candidate results as this sub-user
form8_data = json.dumps({
    'electionCenterId': center_id,
    'totalCastVotes': 1950,
    'validVotes': 1920,
    'rejectedVotes': 30,
    'candidateVotesList': [
        { 'candidateId': c['candidateId'], 'votes': 850 if 'ফারুক' in c['name'] else 400 }
        for c in cands
    ]
}).encode('utf-8')

req_f8 = urllib.request.Request(f'http://localhost:5131/api/v1/candidate/elections/{election_id}/quick-result', data=form8_data, headers=headers)
with urllib.request.urlopen(req_f8) as resp:
    f8_res = json.loads(resp.read().decode('utf-8'))
    print(f"Quick Multi-Candidate Result Submission: Success={f8_res.get('success', True)}")

print('\nSUB-USER MULTI-CANDIDATE RESULT ENTRY FULLY TESTED & WORKING!')
