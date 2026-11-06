import json, urllib.request

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'

def req(url, data=None, method='GET', headers=None):
    h = headers or {}
    h['X-Tenant-Code'] = TENANT_CODE
    body = None
    if data is not None:
        h['Content-Type'] = 'application/json'
        body = json.dumps(data).encode('utf-8')
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Login
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'admin', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
center_id = '0f0e14b3-b1eb-4f0a-bfe0-b60454e4bdd3'

# 2. Get candidates
candidates = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/candidates', headers=headers)
print('Total contesting candidates:', len(candidates))

sample_votes = [2450, 1890, 730, 310]
votes_list = []
for idx, c in enumerate(candidates):
    v = sample_votes[idx] if idx < len(sample_votes) else 100
    votes_list.append({'candidateId': c['candidateId'], 'votes': v})
    print(f"Candidate: {c['name']} ({c['symbolEmoji']} {c['partyName']}) => {v} votes")

# 3. Submit multi-candidate quick result
sub_res = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/quick-result', {
    'electionCenterId': center_id,
    'candidateVotesList': votes_list,
    'candidateId': 'e2fff660-830e-40a9-ab69-edbf8473e55d'
}, method='POST', headers=headers)
print('\nSubmission response:', sub_res)

# 4. Verify results summary
summary = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/results-summary?candidateId=e2fff660-830e-40a9-ab69-edbf8473e55d', headers=headers)
print('\nPrimary Candidate:', summary['candidateName'], summary['candidateSymbolEmoji'], 'Votes:', summary['candidateTotalVotes'])
print('Runner-Up Candidate:', summary['runnerUpName'], summary['runnerUpSymbolEmoji'], 'Votes:', summary['runnerUpTotalVotes'])
print('Lead Margin:', summary['leadMargin'], 'isLeading:', summary['isLeading'])

print('\nALL CANDIDATES LEADERBOARD:')
for idx, t in enumerate(summary.get('allCandidateTallies', [])):
    pri = ' [OUR CANDIDATE]' if t['isPrimary'] else ''
    print(f" #{idx+1} {t['symbolEmoji']} {t['name']} ({t['partyName']}) - {t['totalVotes']} votes ({t['votePercentage']}%){pri}")

print('\nCENTER STATEMENT BREAKDOWN:')
center = summary['centerResults'][0]
print('Center:', center['centerName'], 'Counted:', center['isCounted'])
for cv in center.get('candidateVotesList', []):
    print(f"   {cv['symbolEmoji']} {cv['candidateName']}: {cv['votes']} votes")

