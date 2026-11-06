# -*- coding: utf-8 -*-
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
        if resp.status == 204:
            return None
        return json.loads(resp.read().decode('utf-8'))

auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'

print('=== 1. TEST POST /api/v1/candidate/elections/{electionId}/opponents ===')
new_opp = {
    'name': 'মোঃ নজরুল ইসলাম চৌধুরী',
    'partyName': 'বাংলাদেশ আওয়ামী লীগ',
    'symbolId': 2, # নৌকা
    'slogan': 'উন্নয়ন ও অগ্রযাত্রার প্রতীক',
    'phone': '01811223344'
}

res = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/opponents', new_opp, method='POST', headers=headers)
print('Opponent candidate created successfully:')
print('  ID:', res.get('candidateId'))
print('  Name:', res.get('name'))
print('  Party:', res.get('partyName'))
print('  Symbol:', res.get('symbolNameBn'), res.get('symbolEmoji'))
created_opp_id = res['candidateId']

print('\n=== 2. TEST GET /results-summary WITH allCandidateTallies ===')
results = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/results-summary', headers=headers)
tallies = results.get('allCandidateTallies', [])
print(f'Total candidates contesting in this election: {len(tallies)}')
for t in tallies:
    prim_tag = ' [★ আমাদের প্রার্থী]' if t['isPrimary'] else ''
    print(f"  - {t['name']} ({t['partyName']}) | প্রতীক: {t['symbolName']} ({t['symbolEmoji']}) | ভোট: {t['totalVotes']}{prim_tag}")

assert any(t['candidateId'] == created_opp_id for t in tallies), 'Created opponent candidate should be in tallies!'

print('\n=== 3. TEST DELETE /opponents PREVENT DELETING PRIMARY CANDIDATE ===')
primary_id = results['candidateId']
try:
    req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/opponents/{primary_id}', method='DELETE', headers=headers)
    print('ERROR: Should have rejected primary candidate deletion!')
except urllib.error.HTTPError as e:
    err_body = json.loads(e.read().decode('utf-8'))
    print('Successfully rejected with message:', err_body.get('message'))
    assert e.code == 400

print('\n=== 4. TEST DELETE /opponents FOR OPPONENT CANDIDATE ===')
del_res = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/opponents/{created_opp_id}', method='DELETE', headers=headers)
print('Opponent removed successfully!')

results2 = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/results-summary', headers=headers)
tallies2 = results2.get('allCandidateTallies', [])
print(f'Remaining candidates count: {len(tallies2)}')
assert all(t['candidateId'] != created_opp_id for t in tallies2), 'Opponent should be removed!'

print('\n*** ALL OPPONENT CANDIDATE TESTS PASSED 100%! ***')

