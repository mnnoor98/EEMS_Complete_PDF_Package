import urllib.request
import json
import uuid

# 1. Login as candidate user 'noor'
login_url = 'http://localhost:5131/api/v1/auth/login'
login_data = json.dumps({'tenantId': '1000000000', 'username': 'noor', 'password': 'EEMS@123456!'}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))['accessToken']

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2. Fetch team users
print('Fetching candidate team users...')
req_list = urllib.request.Request('http://localhost:5131/api/v1/candidate/team-users', headers=headers)
with urllib.request.urlopen(req_list) as resp:
    users = json.loads(resp.read().decode('utf-8'))
    print(f'Current team users count: {len(users)}')

# 3. Create a sub-user under this candidate
print('Creating new sub-user under candidate...')
sub_uname = f'agent_{uuid.uuid4().hex[:6]}'
create_data = json.dumps({
    'username': sub_uname,
    'displayName': 'মাঠ সমন্বয়ক তারেক',
    'phone': '01711223344',
    'email': f'{sub_uname}@campaign.local',
    'password': 'Password123!',
    'role': 'ফিল্ড কো-অর্ডিনেটর'
}).encode('utf-8')

req_create = urllib.request.Request('http://localhost:5131/api/v1/candidate/team-users', data=create_data, headers=headers)
with urllib.request.urlopen(req_create) as resp:
    new_user = json.loads(resp.read().decode('utf-8'))
    print(f"Created Sub-User: {new_user['displayName']} ({new_user['username']}), Active={new_user['isActive']}")

# 4. Test logging in as the newly created sub-user
print('Testing login as the new sub-user...')
sub_login_data = json.dumps({'tenantId': '1000000000', 'username': sub_uname, 'password': 'Password123!'}).encode('utf-8')
sub_login_req = urllib.request.Request(login_url, data=sub_login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(sub_login_req) as resp:
    sub_resp = json.loads(resp.read().decode('utf-8'))
    sub_token = sub_resp['accessToken']
    print(f"Sub-user logged in successfully! CandidateId={sub_resp.get('candidateId')}, CandidateName={sub_resp.get('candidateName')}")

# 5. Verify sub-user can access Candidate War Room API (Voters)
sub_headers = {'Authorization': f'Bearer {sub_token}', 'Content-Type': 'application/json'}
election_id = "eade9993-71f5-4bbc-b92c-b636333a2714"
req_voters = urllib.request.Request(f'http://localhost:5131/api/v1/candidate/elections/{election_id}/voters', headers=sub_headers)
with urllib.request.urlopen(req_voters) as resp:
    voters_res = json.loads(resp.read().decode('utf-8'))
    print(f"Sub-user accessed War Room voters successfully! Total voters in candidate scope: {len(voters_res)}")

print('\n======================================================')
print('ALL SUB-USER ARCHITECTURE FLOW VERIFIED AND WORKING 100%!')
print('======================================================')

