import json
import urllib.request
import mimetypes
import uuid

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'
ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
CENTER_ID = '07d5beff-ca28-406a-a1fb-673e3514a6ec' # Boroia Ali Akbar High School

# 1. Login
auth_data = json.dumps({'tenantId': TENANT_CODE, 'username': 'admin', 'password': 'EEMS@123456!'}).encode('utf-8')
req = urllib.request.Request(f'{BASE_URL}/api/v1/auth/login', data=auth_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))['accessToken']

headers = {'Authorization': f'Bearer {token}'}

# Helper to build multipart request
def post_multipart(url, fields, file_field, filename, file_bytes, content_type='text/csv'):
    boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
    body = bytearray()
    for k, v in fields.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode('utf-8'))
        body.extend(f'{v}\r\n'.encode('utf-8'))
    
    body.extend(f'--{boundary}\r\n'.encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode('utf-8'))
    body.extend(f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'))
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(url, data=bytes(body), headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

# Download template
req_tmpl = urllib.request.Request(f'{BASE_URL}/api/v1/candidate/voters/sample-template', headers=headers)
with urllib.request.urlopen(req_tmpl) as resp:
    csv_bytes = resp.read()

# 2. Test Preview
preview = post_multipart(
    f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voters/bulk-preview',
    {'centerId': CENTER_ID},
    'file',
    'sample_voters.csv',
    csv_bytes,
    'text/csv'
)
print('--- BULK PREVIEW ---')
print(f"Total Found: {preview['totalFound']}, Valid: {preview['validCount']}, Format: {preview['detectedFormat']}")
for r in preview['rows'][:3]:
    print(f"  SL: {r['serialNumber']} | NID: {r['voterNumber']} | Name: {r['fullName']} | Area: {r['areaName']} | Valid: {r['isValid']}")

# 3. Test Bulk Import
import_res = post_multipart(
    f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voters/bulk-import-file',
    {'centerId': CENTER_ID},
    'file',
    'sample_voters.csv',
    csv_bytes,
    'text/csv'
)
print('--- BULK IMPORT ---')
print(f"Success: {import_res['success']}, Inserted: {import_res['insertedCount']}, Skipped: {import_res['skippedCount']}")
print(f"Message: {import_res['message']}")

