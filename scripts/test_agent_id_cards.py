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

# 2. Get booth agents
agents = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/booth-agents', headers=headers)
print(f'Total Polling Agents retrieved: {len(agents)}')
for idx, a in enumerate(agents):
    print(f"Agent #{idx+1}: {a['fullName']} | Type: {a['agentType']} | Center: {a['centerName']} ({a['centerCode']}) | Booth: {a['boothName']} | NID: {a['nidNumber']} | Phone: {a['phone']}")

assert len(agents) > 0, "Should have at least 1 booth agent"
print(">>> Booth agents verified successfully for Photo ID Card generation! <<<")

