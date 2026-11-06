import urllib.request
import json
import uuid

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'
ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
CENTER_ID = '0f0e14b3-b1eb-4f0a-bfe0-b60454e4bdd3' # election_center_id

auth_data = json.dumps({'tenantId': TENANT_CODE, 'username': 'admin', 'password': 'EEMS@123456!'}).encode('utf-8')
req = urllib.request.Request(f'{BASE_URL}/api/v1/auth/login', data=auth_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))['accessToken']

req_tmpl = urllib.request.Request(f'{BASE_URL}/api/v1/candidate/voters/sample-template', headers={'Authorization': 'Bearer ' + token})
with urllib.request.urlopen(req_tmpl) as resp:
    csv_bytes = resp.read()

boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
lines = [
    f'--{boundary}',
    'Content-Disposition: form-data; name="centerId"',
    '',
    CENTER_ID,
    f'--{boundary}',
    'Content-Disposition: form-data; name="file"; filename="sample.csv"',
    'Content-Type: text/csv',
    '',
    ''
]
head = '\r\n'.join(lines).encode('utf-8')
tail = f'\r\n--{boundary}--\r\n'.encode('utf-8')
body = head + csv_bytes + tail

req2 = urllib.request.Request(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voters/bulk-import-file', data=body, headers={
    'Authorization': f'Bearer {token}',
    'Content-Type': f'multipart/form-data; boundary={boundary}'
}, method='POST')

try:
    with urllib.request.urlopen(req2) as resp:
        print('SUCCESS:', resp.status, resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP ERROR:', e.code, e.read().decode('utf-8'))
except Exception as e:
    print('EXCEPTION:', e)

