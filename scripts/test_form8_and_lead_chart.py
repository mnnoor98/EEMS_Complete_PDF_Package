import json, urllib.request

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'

def req(url, data=None, method='GET', headers=None):
    h = headers.copy() if headers else {}
    h['X-Tenant-Code'] = TENANT_CODE
    body = None
    if data is not None:
        h['Content-Type'] = 'application/json'
        body = json.dumps(data).encode('utf-8')
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Login
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
cand_id = 'e2fff660-830e-40a9-ab69-edbf8473e55d'

# 2. Get results summary
summary = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/results-summary?candidateId={cand_id}', headers=headers)

print("=== RESULTS SUMMARY FOR FORM-8 & GRAPHICAL LEAD TRACKER ===")
print(f"Total Centers: {summary['totalCenters']}, Counted: {summary['countedCenters']}")
print(f"Our Candidate: {summary['candidateName']} ({summary['candidateSymbolEmoji']}) - {summary['candidateTotalVotes']} votes")
print(f"Top Rival: {summary['runnerUpName']} ({summary['runnerUpSymbolEmoji']}) - {summary['runnerUpTotalVotes']} votes")
print(f"Lead Margin: {summary['leadMargin']} votes (isLeading: {summary['isLeading']})")

print("\n--- ALL CANDIDATES TALLY (FOR VOTE SHARE BARS) ---")
for t in summary.get('allCandidateTallies', []):
    pri = ' [OUR CANDIDATE]' if t['isPrimary'] else ''
    print(f" #{t['symbolEmoji']} {t['name']} ({t['partyName']}): {t['totalVotes']} votes ({t['votePercentage']}%){pri}")

print("\n--- CENTER DATA FOR STATUTORY FORM-8 STATEMENT ---")
for cr in summary.get('centerResults', []):
    print(f"Center: {cr['centerName']} ({cr['centerCode']}) - Counted: {cr['isCounted']}, Form8Verified: {cr['form8Verified']}")
    print(f"  Presiding Officer: {cr.get('presidingOfficerName')}")
    print(f"  Cancelled Votes: {cr.get('cancelledVotes')}")
    print(f"  Candidate Votes List ({len(cr.get('candidateVotesList', []))} candidates):")
    for cv in cr.get('candidateVotesList', []):
        print(f"    - {cv['symbolEmoji']} {cv['candidateName']}: {cv['votes']} votes")

print("\n>>> ALL DATA READY FOR FORM-8 STATEMENT SHEET & GRAPHICAL LEAD TRACKER! <<<")

